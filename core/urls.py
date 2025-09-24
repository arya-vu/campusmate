from django.urls import path, include
from .views import login_view, student_dashboard, faculty_dashboard, hod_dashboard, gatepass_dashboard, item_recovery_dashboard, medical_dashboard, request_dashboard,logout_view
from django.contrib.auth import views as auth_views
from core import views
from django.contrib import messages

urlpatterns = [
   # path('login/', login_view, name='login'),
    path('student-dashboard/', student_dashboard, name='student_dashboard'),
    path('faculty-dashboard/', faculty_dashboard, name='faculty_dashboard'),
    
    path('gatepass-dashboard/', gatepass_dashboard, name='gatepass_dashboard'),
    path('item-recovery-dashboard/', item_recovery_dashboard, name='item_recovery_dashboard'),
    path('medical-dashboard/', medical_dashboard, name='medical_dashboard'),
    path('request-dashboard/', request_dashboard, name='request_dashboard'),
    path('logout/', logout_view, name='logout_view'),
  
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'), name='password_change_done'),
    path('profile/', views.student_profile, name='student_profile'),
    
path('profile/<int:student_id>/', views.student_profile, name='view_student_profile'),

    path('faculty/approve/<int:pk>/', views.approve_gatepass, name='approve_gatepass'),
    path('faculty/reject/<int:pk>/', views.reject_gatepass, name='reject_gatepass'),

    path('hod-dashboard/', views.hod_dashboard, name='hod_dashboard'),
    path('approve-hod/<int:pk>/', views.approve_hod_gatepass, name='approve_hod_gatepass'),
    path('reject-hod/<int:pk>/', views.reject_hod_gatepass, name='reject_hod_gatepass'),

    #path('view-gatepass/<int:pk>/', views.view_gatepass, name='view_gatepass'),
     path('view-gatepass/<int:pk>/', views.view_gatepass, name='view_gatepass'),
     path('view-gatepass-qr/<int:pk>/', views.view_gatepass_qr, name='view_gatepass_qr'),

   
     
      path('faculty/update-leave/<int:pk>/', views.update_leave, name='update_leave'),

    path('faculty/assign_incharge/<int:pk>/', views.assign_incharge, name='assign_incharge'),



]
