
from django.shortcuts import render, get_object_or_404
#from .models import StudentProfile, FacultyProfile, HODProfile, GatepassRequest
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth import authenticate, login,logout
from django.shortcuts import render, redirect
from .models import UserProfile
import json
from django.shortcuts import render, get_object_or_404
from .models import GatepassRequest, StudentProfile
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib import messages

from datetime import datetime, date

import base64

from .models import UserProfile, StudentProfile, GatepassRequest, Request, MedicalAppointment, ItemRecovery
from io import BytesIO
from django.http import HttpResponse

import qrcode

def student_dashboard(request):
    student = request.user.userprofile.student_profile  # Get the logged-in student
    gatepasses = GatepassRequest.objects.filter(student=student)

    # Summary counts
    pending_count = gatepasses.filter(hod_status='Pending').count()
    approved_count = gatepasses.filter(hod_status='Approved').count()
    rejected_count = gatepasses.filter(hod_status='Rejected').count()

    # Chart data
    chart_labels = ['Personal', 'Medical', 'Other']
    chart_data = [
        gatepasses.filter(reason='Personal').count(),
        gatepasses.filter(reason='Medical').count(),
        gatepasses.filter(reason='Other').count(),
    ]

    return render(request, 'core/student_dashboard.html', {
        'student': student,
        'gatepasses': gatepasses,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    })



def faculty_dashboard(request):
    user_profile = request.user.userprofile

    # -----------------------------
    # Current Gatepass Requests
    # -----------------------------
    requests = GatepassRequest.objects.filter(faculty=user_profile).order_by('-date', '-time')

    pending_count = requests.filter(faculty_status='Pending').count()
    approved_count = requests.filter(faculty_status='Approved').count()
    rejected_count = requests.filter(faculty_status='Rejected').count()

    # -----------------------------
    # Reason-wise aggregation
    # -----------------------------
    reason_agg = requests.values('reason').annotate(count=Count('id'))
    reason_labels = [r['reason'] for r in reason_agg]
    reason_counts = [r['count'] for r in reason_agg]

    # -----------------------------
    # Day-wise aggregation
    # -----------------------------
    day_agg = requests.values('date').annotate(count=Count('id')).order_by('date')
    day_labels = [d['date'].strftime('%b %d') if isinstance(d['date'], date) else str(d['date']) for d in day_agg]
    day_counts = [d['count'] for d in day_agg]

    # -----------------------------
    # Status-wise aggregation
    # -----------------------------
    status_agg = requests.values('faculty_status').annotate(count=Count('id'))
    status_labels = [s['faculty_status'] for s in status_agg]
    status_counts = [s['count'] for s in status_agg]

    # -----------------------------
    # Student Request History
    # -----------------------------
    all_requests = GatepassRequest.objects.filter(faculty=user_profile).order_by('-date', '-time')

    # -----------------------------
    # Leave & In-Charge Faculty
    # -----------------------------
    leave_faculty = getattr(user_profile, 'on_leave', False)
    incharge_faculty = getattr(user_profile, 'incharge_faculty', None)

    # -----------------------------
    # Notifications (example: last 5 pending requests)
    # -----------------------------
    notifications = []
    pending_notifications = requests.filter(faculty_status='Pending').order_by('-date')[:5]
    for req in pending_notifications:
        notifications.append({
            'message': f"New gatepass request from {req.student.user_profile.user.get_full_name()}",
            'timestamp': req.date
        })

    # -----------------------------
    # Context for template
    # -----------------------------
    context = {
        'requests': requests,
        'all_requests': all_requests,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'reason_labels': json.dumps(reason_labels),
        'reason_counts': json.dumps(reason_counts),
        'day_labels': json.dumps(day_labels),
        'day_counts': json.dumps(day_counts),
        'status_labels': json.dumps(status_labels),
        'status_counts': json.dumps(status_counts),
        'leave_faculty': leave_faculty,
        'incharge_faculty': incharge_faculty,
        'notifications': notifications,
    }

    return render(request, 'core/faculty_dashboard.html', context)





# HOD Dashboard
def hod_dashboard(request):
    # Get HOD profile of logged-in user
    hod_profile = UserProfile.objects.get(user=request.user)

    # Fetch requests that are approved by faculty but pending at HOD
    pending_hod_requests = GatepassRequest.objects.filter(
        hod_status='Pending',
        faculty_status='Approved'
    ).order_by('-date', '-time')

    context = {
        'requests': pending_hod_requests
    }
    return render(request, 'core/hod_dashboard.html', context)


def approve_hod_gatepass(request, pk):
    gatepass = get_object_or_404(GatepassRequest, id=pk)
    gatepass.hod_status = 'Approved'
    gatepass.hod = request.user.userprofile  # store HOD approving
    gatepass.save()
    messages.success(request, "Gatepass finally approved by HOD!")
    return redirect('hod_dashboard')  # ✅ Correct




def reject_hod_gatepass(request, pk):
    gatepass = get_object_or_404(GatepassRequest, id=pk)
    gatepass.hod_status = 'Rejected'
    gatepass.save()
    messages.error(request, "Gatepass rejected by HOD!")
    return redirect('hod_dashboard')  # ✅ Correct



def item_recovery_dashboard(request):
    return render(request, 'core/item_recovery_dashboard.html')

def medical_dashboard(request):
    return render(request, 'core/medical_dashboard.html')




def gatepass_dashboard(request):
    student = request.user.userprofile.student_profile  
    gatepasses = GatepassRequest.objects.filter(student=student)

    # Summary counts
    pending_count = gatepasses.filter(hod_status='Pending').count()
    approved_count = gatepasses.filter(hod_status='Approved').count()
    rejected_count = gatepasses.filter(hod_status='Rejected').count()

    # ✅ Dynamic reason-wise aggregation
    reason_agg = gatepasses.values('reason').annotate(count=Count('id'))
    chart_labels = [r['reason'] for r in reason_agg]
    chart_data = [r['count'] for r in reason_agg]

    return render(request, 'core/gatepass_dashboard.html', {
        'gatepasses': gatepasses,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    })



def request_dashboard(request):
    # Get real faculty users from DB
    faculties = UserProfile.objects.filter(role='faculty')

    if request.method == 'POST':
        selected_faculty_id = request.POST.get('faculty')
        reason = request.POST.get('reason')
        date_input = request.POST.get('date')
        time_input = request.POST.get('time')
        request_type = request.POST.get('request_type')  # New field

        if not selected_faculty_id or not reason or not date_input or not time_input or not request_type:
            messages.error(request, "Please fill all fields.")
            return redirect('request_dashboard')

        # Convert date and time strings to Python objects
        try:
            date_obj = datetime.strptime(date_input, "%Y-%m-%d").date()
            time_obj = datetime.strptime(time_input, "%H:%M").time()
        except ValueError:
            messages.error(request, "Invalid date or time format.")
            return redirect('request_dashboard')

        # Enforce 1-day rule for normal requests
        today = timezone.localdate()
        emergency_flag = False
        if request_type == 'normal':
            if date_obj < today + timezone.timedelta(days=1):
                messages.error(request, "Normal gatepass requests must be submitted at least 1 day in advance.")
                return redirect('request_dashboard')
        elif request_type == 'emergency':
            emergency_flag = True
        else:
            messages.error(request, "Invalid request type.")
            return redirect('request_dashboard')

        # Get student profile
        student_profile = request.user.userprofile.student_profile

        # Get selected faculty profile
        faculty_profile = UserProfile.objects.get(id=selected_faculty_id)

        # Save GatepassRequest
        GatepassRequest.objects.create(
            student=student_profile,
            faculty=faculty_profile,
            reason=reason,
            date=date_obj,
            time=time_obj,
            request_type=request_type,
            emergency=emergency_flag
        )

        messages.success(request, f"Gatepass request sent to {faculty_profile.user.username}.")
        return redirect('request_dashboard')

    context = {
        'faculties': faculties,
        'today': timezone.localdate()  # restrict past dates in the form
    }
    return render(request, 'core/request_dashboard.html', context)


def view_gatepass(request, pk):
    gatepass = get_object_or_404(GatepassRequest, id=pk)
    qr_code_img = None

    if gatepass.hod_status == 'Approved':
        # Data to encode in QR
        qr_data = f"""
        Student: {gatepass.student.user_profile.user.get_full_name()}
        Department: {gatepass.student.course}
        Semester: {gatepass.student.semester}
        Approved Faculty: {gatepass.faculty.user.get_full_name()}
        HOD Approval Time: {gatepass.hod_approval_time}
        Exit Time: {gatepass.time}
        """
        # Generate QR
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')

        # Convert to base64 for template
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_code_img = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'core/view_gatepass.html', {
        'gatepass': gatepass,
        'qr_code': qr_code_img
    })



def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)  # ✅ log the user in
            
            try:
                profile = UserProfile.objects.get(user=user)
                user_role = profile.role
            except UserProfile.DoesNotExist:
                messages.error(request, "No profile found for this user.")
                return redirect('login')

            # ✅ Redirect based on role
            if user_role == 'student':
                return redirect('student_dashboard')
            elif user_role == 'faculty':
                return redirect('faculty_dashboard')
            elif user_role == 'hod':
                return redirect('hod_dashboard')
            else:
                messages.error(request, "Invalid user role.")
                return redirect('login')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')
    
    return render(request, 'login.html')




def logout_view(request):
    logout(request)
    return redirect('login')

def my_view(request):
    form = MyForm(request.POST or None)
    return render(request, 'core/password_reset.html', {'form': form})

def student_profile(request, student_id=None):
    if student_id:
        # Faculty or HOD accessing a specific student
        student = get_object_or_404(StudentProfile, id=student_id)
    else:
        # Student accessing their own profile
        student = get_object_or_404(StudentProfile, user_profile=request.user.userprofile)

    # Get approved gatepass
    approved_gatepass = GatepassRequest.objects.filter(student=student, hod_status='Approved').last()

    qr_code_base64 = None
    if approved_gatepass:
        qr_data = (
            f"Student: {student.user_profile.user.get_full_name()}\n"
            f"Department: {student.course}\n"
            f"Semester: {student.semester}\n"
            f"Approved Faculty: {approved_gatepass.faculty.user.get_full_name()}\n"
            f"HOD Approval Time: {approved_gatepass.hod_approval_time}\n"
            f"Exit Time: {approved_gatepass.date} {approved_gatepass.time}"
        )
        qr_img = qrcode.make(qr_data)
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'core/student_profile.html', {
        'student': student,
        'approved_gatepass': approved_gatepass,
        'qr_code': qr_code_base64
    })



def approve_gatepass(request, pk):
    gatepass = get_object_or_404(GatepassRequest, pk=pk)

    if request.user.userprofile.role == 'faculty':
        gatepass.faculty_status = 'Approved'
        gatepass.approved_faculty = request.user.userprofile
        gatepass.faculty_approval_time = timezone.now()
        gatepass.save()
        messages.success(request, "Gatepass approved by Faculty!")
        return redirect('faculty_dashboard')

    elif request.user.userprofile.role == 'hod':
        gatepass.hod_status = 'Approved'
        gatepass.hod_approval_time = timezone.now()
        gatepass.save()
        messages.success(request, "Gatepass approved by HOD!")
        return redirect('hod_dashboard')

    else:
        messages.error(request, "You are not authorized to approve this gatepass.")
        return redirect('gatepass_dashboard')


def reject_gatepass(request, pk):
    gatepass = get_object_or_404(GatepassRequest, pk=pk)

    if request.user.userprofile.role == 'faculty':
        gatepass.faculty_status = 'Rejected'
        gatepass.approved_faculty = None
        gatepass.faculty_approval_time = None
        messages.error(request, "Gatepass rejected by Faculty!")
        return redirect('faculty_dashboard')

    elif request.user.userprofile.role == 'hod':
        gatepass.hod_status = 'Rejected'
        gatepass.hod_approval_time = None
        messages.error(request, "Gatepass rejected by HOD!")
        return redirect('hod_dashboard')

    return redirect('gatepass_dashboard')





def generate_gatepass_qr(request, pk):
    gatepass = get_object_or_404(GatepassRequest, id=pk)

    if gatepass.hod_status != 'Approved':
        messages.error(request, "Gatepass not approved yet.")
        return redirect('student_dashboard')

    student = gatepass.student
    faculty_name = gatepass.faculty.user.username
    approval_time = gatepass.hod_approval_time if hasattr(gatepass, 'hod_approval_time') else datetime.now()

    qr_data = (
        f"Student: {student.user_profile.user.get_full_name()}\n"
        f"Department: {student.course}\n"
        f"Semester: {student.semester}\n"
        f"Approved Faculty: {faculty_name}\n"
        f"HOD Approval Time: {approval_time}\n"
        f"Exit Time: {gatepass.date} {gatepass.time}"
    )

    qr_img = qrcode.make(qr_data)
    buffer = BytesIO()
    qr_img.save(buffer, format='PNG')
    buffer.seek(0)

    return HttpResponse(buffer, content_type='image/png')


import qrcode
import io
import base64
from django.http import HttpResponse
from django.utils import timezone
from .models import GatepassRequest

def view_gatepass_qr(request, pk):
    gatepass = GatepassRequest.objects.get(id=pk)

    # Collect QR data
    qr_data = f"""
    Name: {gatepass.student.user_profile.user.get_full_name()}
    Department: {gatepass.student.course}
    Semester: {gatepass.student.semester}
    Approved Faculty: {gatepass.faculty.user.get_full_name()}
    HOD Approval Time: {gatepass.hod_approval_time}
    Exit Time: {gatepass.time}
    """

    # Check validity
    now = timezone.localtime(timezone.now())
    exit_datetime = timezone.datetime.combine(gatepass.date, gatepass.time)
    exit_datetime = timezone.make_aware(exit_datetime)  # make timezone aware
    if now > exit_datetime:
        qr_data += "\nSTATUS: EXPIRED"
    else:
        qr_data += "\nSTATUS: VALID"

    # Generate QR code
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to BytesIO
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return HttpResponse(buffer, content_type="image/png")


def update_leave(request, pk):
    faculty = get_object_or_404(UserProfile, pk=pk)

    if request.method == 'POST':
        faculty.on_leave = 'on_leave' in request.POST
        faculty.leave_start = request.POST.get('leave_start')
        faculty.leave_end = request.POST.get('leave_end')
        faculty.save()
        messages.success(request, "Leave status updated!")
        return redirect('faculty_dashboard')

    return redirect('faculty_dashboard')



def assign_incharge(request, pk):
    # pk = faculty id who is on leave
    faculty_on_leave = get_object_or_404(UserProfile, pk=pk)
    faculties = UserProfile.objects.filter(role='faculty').exclude(pk=pk)
    
    if request.method == 'POST':
        selected_faculty_id = request.POST.get('incharge_faculty')
        incharge_faculty = get_object_or_404(UserProfile, pk=selected_faculty_id)
        faculty_on_leave.incharge_faculty = incharge_faculty
        faculty_on_leave.save()
        messages.success(request, f"{incharge_faculty.user.username} assigned as in-charge.")
        return redirect('faculty_dashboard')
    
    return render(request, 'core/assign_incharge.html', {'faculty_on_leave': faculty_on_leave, 'faculties': faculties})
