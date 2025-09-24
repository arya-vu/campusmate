from django.contrib import admin
from django.urls import path, include
from core.views import login_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='login'),         # root login
    path('', include('core.urls')),             # include all dashboard URLs as they are
    #path('accounts/', include('django.contrib.auth.urls')),
    
]