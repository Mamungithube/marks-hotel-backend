# ==========================================
# authontication/views.py - UPDATED VERSION
# ==========================================

from rest_framework import generics, status, permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.db.models import Count

# ✅ Import থেকে Custom User
from .models import User
from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    OTPVerificationSerializer, ResendOTPSerializer,
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer, UserProfileUpdateSerializer
)
import random
import string


# ==========================================
# HELPER FUNCTION FOR OTP
# ==========================================

def generate_otp():
    """Generate 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))


def send_otp_email(user, otp):
    """Send OTP via email"""
    try:
        # Simple text email
        subject = f'Email Verification - OTP: {otp}'
        message = f'''
Hello {user.get_full_name()},

Your OTP for email verification is: {otp}

This OTP will expire in 10 minutes.

If you didn't register, please ignore this email.

Thanks,
Hotel Management Team
        '''
        
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        
        # OR HTML email (if you have template)
        # email_body = render_to_string('emails/otp_email.html', {
        #     'user': user,
        #     'otp': otp
        # })
        # email = EmailMultiAlternatives(subject, '', settings.EMAIL_HOST_USER, [user.email])
        # email.attach_alternative(email_body, 'text/html')
        # email.send()
        
    except Exception as e:
        print(f"Email sending failed: {e}")


# ==========================================
# 1. USER REGISTRATION
# ==========================================

class UserRegistrationView(generics.CreateAPIView):
    """
    User Registration with OTP
    POST /api/v1/auth/register/
    
    Body:
    {
        "email": "customer@test.com",
        "password": "Test@123",
        "password2": "Test@123",
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+8801712345678"
    }
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # User already created with OTP in serializer
        
        # Send OTP email
        send_otp_email(user, user.otp)
        
        return Response({
            'message': 'Registration successful. Please check your email for OTP verification.',
            'email': user.email,
            'user_id': str(user.id)
        }, status=status.HTTP_201_CREATED)


# ==========================================
# 2. OTP VERIFICATION
# ==========================================

class OTPVerificationView(APIView):
    """
    Verify OTP
    POST /api/v1/auth/verify-otp/
    
    Body:
    {
        "email": "customer@test.com",
        "otp": "123456"
    }
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Mark user as verified
        user.is_verified = True
        user.email_verified_at = timezone.now()
        user.otp = None
        user.otp_created_at = None
        user.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Email verified successfully!',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)


# ==========================================
# 3. RESEND OTP
# ==========================================

class ResendOTPView(APIView):
    """
    Resend OTP
    POST /api/v1/auth/resend-otp/
    
    Body:
    {
        "email": "customer@test.com"
    }
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # Generate new OTP
        user.otp = generate_otp()
        user.otp_created_at = timezone.now()
        user.save()
        
        # Send OTP email
        send_otp_email(user, user.otp)
        
        return Response({
            'message': 'New OTP sent successfully to your email.'
        }, status=status.HTTP_200_OK)


# ==========================================
# 4. JWT LOGIN
# ==========================================

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    JWT Login
    POST /api/v1/auth/login/
    
    Body:
    {
        "email": "customer@test.com",
        "password": "Test@123"
    }
    
    Response:
    {
        "access": "eyJ0eXAiOiJKV1QiLCJh...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJh...",
        "user": {
            "id": "uuid",
            "email": "customer@test.com",
            "user_type": "customer",
            "role": "Customer"
        }
    }
    """
    serializer_class = CustomTokenObtainPairSerializer


# ==========================================
# 5. LOGOUT
# ==========================================

class LogoutView(APIView):
    """
    Logout - Blacklist refresh token
    POST /api/v1/auth/logout/
    
    Body:
    {
        "refresh": "your_refresh_token_here"
    }
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({
                    'error': 'Refresh token is required.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({
                'message': 'Logout successful.'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Invalid token or already blacklisted.'
            }, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 6. CHANGE PASSWORD
# ==========================================

class ChangePasswordView(APIView):
    """
    Change Password
    POST /api/v1/auth/change-password/
    
    Body:
    {
        "old_password": "Test@123",
        "new_password": "NewTest@123",
        "new_password2": "NewTest@123"
    }
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'message': 'Password changed successfully.'
        }, status=status.HTTP_200_OK)


# ==========================================
# 7. FORGOT PASSWORD (Reset via OTP)
# ==========================================

class ForgotPasswordView(APIView):
    """
    Forgot Password - Send reset OTP
    POST /api/v1/auth/forgot-password/
    
    Body:
    {
        "email": "customer@test.com"
    }
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({
                'error': 'Email is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email.lower())
        except User.DoesNotExist:
            return Response({
                'error': 'Email not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Generate OTP
        user.otp = generate_otp()
        user.otp_created_at = timezone.now()
        user.save()
        
        # Send email
        send_mail(
            'Password Reset OTP',
            f'Your password reset OTP is: {user.otp}\n\nValid for 10 minutes.',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        
        return Response({
            'message': 'Password reset OTP sent to your email.'
        }, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    """
    Reset Password with OTP
    POST /api/v1/auth/reset-password/
    
    Body:
    {
        "email": "customer@test.com",
        "otp": "123456",
        "new_password": "NewTest@123"
    }
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')
        
        if not all([email, otp, new_password]):
            return Response({
                'error': 'Email, OTP, and new password are required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email.lower())
        except User.DoesNotExist:
            return Response({
                'error': 'Invalid email.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if user.otp != otp or not user.is_otp_valid:
            return Response({
                'error': 'Invalid or expired OTP.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Reset password
        user.set_password(new_password)
        user.otp = None
        user.otp_created_at = None
        user.save()
        
        return Response({
            'message': 'Password reset successful. You can now login.'
        }, status=status.HTTP_200_OK)


# ==========================================
# 8. USER PROFILE
# ==========================================

class UserProfileView(generics.RetrieveAPIView):
    """
    Get User Profile
    GET /api/v1/auth/profile/
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserProfileUpdateView(generics.UpdateAPIView):
    """
    Update User Profile
    PUT/PATCH /api/v1/auth/profile/update/
    
    Body:
    {
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+8801712345678",
        "address": "Dhaka, Bangladesh"
    }
    """
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


# ==========================================
# 9. USER MANAGEMENT (Admin Only)
# ==========================================

class UserViewSet(viewsets.ModelViewSet):
    """
    User Management ViewSet (Admin Only)
    
    List: GET /api/v1/auth/users/
    Create: POST /api/v1/auth/users/
    Detail: GET /api/v1/auth/users/<id>/
    Update: PUT/PATCH /api/v1/auth/users/<id>/
    Delete: DELETE /api/v1/auth/users/<id>/
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()
    
    def get_queryset(self):
        """Filter based on query params"""
        queryset = User.objects.all()
        
        # Filter by user type
        user_type = self.request.query_params.get('user_type', None)
        if user_type:
            queryset = queryset.filter(user_type=user_type)
        
        # Filter by verification status
        is_verified = self.request.query_params.get('is_verified', None)
        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified == 'true')
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active == 'true')
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Manually verify a user (Admin only)"""
        user = self.get_object()
        user.is_verified = True
        user.email_verified_at = timezone.now()
        user.save()
        
        return Response({
            'message': f'User {user.email} verified successfully.'
        })
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate user (Admin only)"""
        user = self.get_object()
        user.is_active = True
        user.save()
        
        return Response({'message': f'User {user.email} activated.'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate user (Admin only)"""
        user = self.get_object()
        user.is_active = False
        user.save()
        
        return Response({'message': f'User {user.email} deactivated.'})


# ==========================================
# 10. STATISTICS & UTILITIES
# ==========================================

class RegisteredUsersCountView(APIView):
    """
    Get registered users count
    GET /api/v1/auth/users-count/
    
    Query params:
    - user_type: customer/staff/finance/admin
    - is_verified: true/false
    """
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        # Total users
        total_users = User.objects.count()
        
        # By user type
        customers = User.objects.filter(user_type=User.CUSTOMER).count()
        staff = User.objects.filter(user_type=User.STAFF).count()
        finance = User.objects.filter(user_type=User.FINANCE).count()
        admins = User.objects.filter(user_type=User.ADMIN).count()
        
        # By status
        verified_users = User.objects.filter(is_verified=True).count()
        active_users = User.objects.filter(is_active=True).count()
        
        return Response({
            'total_users': total_users,
            'by_type': {
                'customers': customers,
                'staff': staff,
                'finance': finance,
                'admins': admins
            },
            'by_status': {
                'verified': verified_users,
                'active': active_users,
                'unverified': total_users - verified_users,
                'inactive': total_users - active_users
            }
        })


class IsAdminStatusView(APIView):
    """
    Check if current user is admin
    GET /api/v1/auth/is-admin/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        return Response({
            'is_admin': request.user.is_admin,
            'is_staff': request.user.is_hotel_staff,
            'is_finance': request.user.is_finance,
            'is_customer': request.user.is_customer,
            'user_type': request.user.user_type,
            'role': request.user.get_user_type_display()
        })

