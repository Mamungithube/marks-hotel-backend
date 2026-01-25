# authontication/urls.py - UPDATED VERSION

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from . import views

router = DefaultRouter()
router.register('users', views.UserViewSet, basename='user')

app_name = 'authontication'

urlpatterns = [
    # Registration & Verification
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('verify-otp/', views.OTPVerificationView.as_view(), name='verify-otp'),
    path('resend-otp/', views.ResendOTPView.as_view(), name='resend-otp'),
    
    # JWT Login/Logout
    path('login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # Password Management
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset-password'),
    
    # Profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='profile-update'),
    
    # Statistics
    path('users-count/', views.RegisteredUsersCountView.as_view(), name='users-count'),
    path('is-admin/', views.IsAdminStatusView.as_view(), name='is-admin'),
    
    # Router URLs (User management - Admin only)
    path('', include(router.urls)),
]