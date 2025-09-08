from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views
from .views import RegisteredUsersCount,UserRegistrationAPIView,activate,UserLoginApiView,UserLogoutApiView,activate,IsAdminStatusAPIView,ChangePasswordViewSet,UserListAPIView,UserProfileView
# from .views import UserProfileView, ChangePasswordViewSet,UserLoginApiView,UserLogoutApiView,RegisteredUsersCount,activate,IsAdminStatusAPIView
router = DefaultRouter()

router.register('list', views.CustomerViewset)
# router.register(r'pass_cng', ChangePasswordViewSet, basename='pass_cng')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationAPIView.as_view(), name='register'),
    path('login/', UserLoginApiView.as_view(), name='login'),
    path('logout/', UserLogoutApiView.as_view(), name='logout'),
    path('api/profile/', UserProfileView.as_view(), name='user-profile'),
    path('active/<uid64>/<token>', activate, name='activate'),
    path('registered-users-count/', RegisteredUsersCount.as_view(), name='registered_users_count'),
    path('admins/', IsAdminStatusAPIView.as_view(), name='admins'),
    path('api/users/', UserListAPIView.as_view(), name='user-list'),
    path('change_pass/',ChangePasswordViewSet.as_view({'post':'create'}), name='change_password'),
]