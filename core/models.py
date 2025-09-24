from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('hod', 'HOD'),
        ('doctor', 'Doctor'),
        ('security', 'Security'),
        ('admin', 'Administrator'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

class StudentProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='student_profile')
    address = models.TextField()
    age = models.PositiveIntegerField()
    course = models.CharField(max_length=100)
    semester = models.CharField(max_length=50)
    year = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.user_profile.user.username} Profile"



class GatepassRequest(models.Model):
    REQUEST_TYPES = [
        ('normal', 'Normal'),
        ('emergency', 'Emergency'),
    ]
    student = models.ForeignKey('StudentProfile', on_delete=models.CASCADE)
    faculty = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='faculty_gatepasses')
    hod = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='hod_gatepasses', null=True, blank=True)
    reason = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES, default='normal')
    faculty_status = models.CharField(max_length=20, default='Pending')
    hod_status = models.CharField(max_length=20, default='Pending')
    emergency = models.BooleanField(default=False)

    # 👇 add this
    hod_approval_time = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if isinstance(self.date, str):
            self.date = datetime.strptime(self.date, "%Y-%m-%d").date()
        if isinstance(self.time, str):
            self.time = datetime.strptime(self.time, "%H:%M").time()

        today = timezone.localdate()
        if self.request_type == 'normal':
            if self.date < today + timezone.timedelta(days=1):
                raise ValidationError("Normal gatepass requests must be submitted at least 1 day in advance.")
            self.emergency = False
        elif self.request_type == 'emergency':
            self.emergency = True
        else:
            raise ValidationError("Invalid request type.")

    def save(self, *args, **kwargs):
    # Only validate when creating a new record
        if not self.pk:  # pk is None → new object
           self.clean()
        super().save(*args, **kwargs)



class Request(models.Model):
    REQUEST_TYPES = [
        ('general', 'General Request'),
        ('complaint', 'Complaint'),
    ]
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.request_type} - {self.title}"






class MedicalAppointment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    doctor = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='doctor_appointments')
    reason = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, default="Pending")

    def __str__(self):
        return f"Appointment - {self.student.user_profile.user.username}"




class ItemRecovery(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=100)
    description = models.TextField()
    found = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Item: {self.item_name} - {self.student.user_profile.user.username}"


class FacultyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    course = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    on_leave = models.BooleanField(default=False)
    leave_start = models.DateField(null=True, blank=True)
    leave_end = models.DateField(null=True, blank=True)

class Notification(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.user.username}"