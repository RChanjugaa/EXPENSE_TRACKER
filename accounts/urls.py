from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import EmailOrUsernameAuthenticationForm

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('verify-registration/', views.verify_registration_otp, name='verify_registration_otp'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
    path('login/otp/', views.request_login_otp, name='request_login_otp'),
    path('login/otp/verify/', views.verify_login_otp, name='verify_login_otp'),
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html',
        authentication_form=EmailOrUsernameAuthenticationForm,
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
