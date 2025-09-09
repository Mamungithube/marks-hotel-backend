from rest_framework.routers import DefaultRouter
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .views import CustomerViewset,RegisteredUsersCount,UserRegistrationAPIView,UserLoginApiView,UserLogoutApiView,IsAdminStatusAPIView,ChangePasswordViewSet,UserListAPIView,UserProfileView,ResendOTPApiView,VerifyOTPApiView

router = DefaultRouter()

router.register('list', CustomerViewset)
# router.register(r'pass_cng', ChangePasswordViewSet, basename='pass_cng')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationAPIView.as_view(), name='register'),
    path('resend_otp/', ResendOTPApiView.as_view(), name='resend-otp'),
    path('verify_otp/', VerifyOTPApiView.as_view(), name='verify-otp'),
    path('login/', UserLoginApiView.as_view(), name='login'),
    path('logout/', UserLogoutApiView.as_view(), name='logout'),
    path('api/profile/', UserProfileView.as_view(), name='user-profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('registered-users-count/', RegisteredUsersCount.as_view(), name='registered_users_count'),
    path('admins/', IsAdminStatusAPIView.as_view(), name='admins'),
    path('api/users/', UserListAPIView.as_view(), name='user-list'),
    path('change_pass/',ChangePasswordViewSet.as_view({'post':'create'}), name='change_password'),
]