from django.contrib import admin
from .models import UserProfile, StudentProfile, GatepassRequest, Request, MedicalAppointment, ItemRecovery

# Register models so they show in Django Admin
admin.site.register(UserProfile)
admin.site.register(StudentProfile)
admin.site.register(GatepassRequest)
admin.site.register(Request)
admin.site.register(MedicalAppointment)
admin.site.register(ItemRecovery)

