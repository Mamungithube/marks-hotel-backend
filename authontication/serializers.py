# from rest_framework import serializers
# from . import models
# from .utils import generate_otp
# from django.contrib.auth.models import User
# from django.contrib.auth import password_validation
# from django.core.mail import send_mail
# from rest_framework_simplejwt.tokens import RefreshToken

# class CustomerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.Customer
#         fields = '__all__'

# class RegistrationSerializer(serializers.ModelSerializer):
#     confirm_password = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ['username', 'first_name', 'last_name', 'email', 'password', 'confirm_password', 'date_joined']
#         extra_kwargs = {
#             'password': {'write_only': True},
#         }

#     def validate(self, data):
#         if data['password'] != data['confirm_password']:
#             raise serializers.ValidationError("Passwords do not match")
#         return data

#     def create(self, validated_data):
#         validated_data.pop('confirm_password')
#         user = User.objects.create_user(**validated_data)
#         user.is_active = False 
#         user.save()

#         otp_code = generate_otp()
#         models.CustomUser.objects.create(user=user, otp=otp_code)

#         email_subject = 'Your OTP Code : '
#         email_body = f'Your OTP Code Is : {otp_code}'
#         send_mail(
#             email_subject,
#             email_body,
#             'mdmamun340921@gmail.com', 
#             [user.email]
#         )
        
#         return user

# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField(required=True)
#     password = serializers.CharField(required=True, write_only=True)

# class UserLoginSerializer(serializers.ModelSerializer):
#     tokens = serializers.SerializerMethodField()
    
#     def get_tokens(self, obj):
#         user = User.objects.get(username=obj['username'])
#         refresh = RefreshToken.for_user(user)
#         return {
#             'refresh': str(refresh),
#             'access': str(refresh.access_token),
#         }
    
#     class Meta:
#         model = User
#         fields = ['username', 'tokens']

# class ChangePasswordSerializer(serializers.Serializer):
#     old_password = serializers.CharField(required=True, write_only=True)
#     new_password = serializers.CharField(required=True, write_only=True)
#     confirm_password = serializers.CharField(required=True, write_only=True)

#     def validate_new_password(self, value):
#         password_validation.validate_password(value, self.context['request'].user)
#         return value

#     def validate(self, data):
#         if data["new_password"] != data["confirm_password"]:
#             raise serializers.ValidationError({"confirm_password": "New password and confirm password do not match."})
#         return data



# from rest_framework import serializers
# from django.contrib.auth.models import User

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'first_name', 'last_name', 'email']
        
#     def to_representation(self, instance):
#         representation = super().to_representation(instance)
#         # ব্রাউজেবল API তে সব ফিল্ড দেখানোর জন্য
#         representation['id'] = instance.id
#         representation['username'] = instance.username
#         representation['first_name'] = instance.first_name
#         representation['last_name'] = instance.last_name
#         representation['email'] = instance.email
#         return representation

# # serializers.py
# from rest_framework import serializers
# from .models import CustomUser

# class CustomUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = '__all__'



# authontication/serializers.py
# ==========================================

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User
import random
import string
from django.utils import timezone


# ==========================================
# 1. USER SERIALIZERS
# ==========================================

class UserSerializer(serializers.ModelSerializer):
    """
    Basic User Serializer - for profile display
    """
    full_name = serializers.SerializerMethodField()
    role = serializers.CharField(source='get_user_type_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'user_type', 'role', 'profile_image',
            'date_of_birth', 'address', 'city', 'country', 'postal_code',
            'is_verified', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'is_verified', 'created_at', 'user_type']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    User Registration Serializer with OTP generation
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password2',
            'first_name', 'last_name', 'phone_number'
        ]
    
    def validate(self, attrs):
        """Validate password match"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs
    
    def validate_email(self, value):
        """Check if email already exists"""
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("Email already registered.")
        return value.lower()
    
    def create(self, validated_data):
        """Create user with OTP"""
        validated_data.pop('password2')
        
        # Generate OTP
        otp = ''.join(random.choices(string.digits, k=6))
        
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            user_type=User.CUSTOMER,  # Default role
            is_verified=False,
            otp=otp,
            otp_created_at=timezone.now()
        )
        
        return user


class OTPVerificationSerializer(serializers.Serializer):
    """
    OTP Verification Serializer
    """
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(max_length=6, required=True)
    
    def validate(self, attrs):
        """Validate OTP"""
        email = attrs.get('email')
        otp = attrs.get('otp')
        
        try:
            user = User.objects.get(email=email.lower())
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email address.")
        
        if user.is_verified:
            raise serializers.ValidationError("Account already verified.")
        
        if not user.otp or user.otp != otp:
            raise serializers.ValidationError("Invalid OTP.")
        
        if not user.is_otp_valid:
            raise serializers.ValidationError("OTP has expired. Please request a new one.")
        
        attrs['user'] = user
        return attrs


class ResendOTPSerializer(serializers.Serializer):
    """
    Resend OTP Serializer
    """
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Check if user exists"""
        try:
            user = User.objects.get(email=value.lower())
            if user.is_verified:
                raise serializers.ValidationError("Account already verified.")
        except User.DoesNotExist:
            raise serializers.ValidationError("Email not registered.")
        
        return value.lower()


# ==========================================
# 2. JWT AUTHENTICATION SERIALIZERS
# ==========================================

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT Token Serializer with additional user data
    """
    def validate(self, attrs):
        """Validate and add user data to token response"""
        data = super().validate(attrs)
        
        # Check if user is verified
        if not self.user.is_verified:
            raise serializers.ValidationError(
                "Please verify your email before logging in."
            )
        
        # Check if user is active
        if not self.user.is_active:
            raise serializers.ValidationError(
                "Your account has been deactivated. Please contact support."
            )
        
        # Add user data to response
        data['user'] = {
            'id': str(self.user.id),
            'email': self.user.email,
            'full_name': self.user.get_full_name(),
            'user_type': self.user.user_type,
            'role': self.user.get_user_type_display(),
            'is_admin': self.user.is_admin,
            'is_customer': self.user.is_customer,
            'is_staff': self.user.is_hotel_staff,
            'is_finance': self.user.is_finance,
        }
        
        return data
    
    @classmethod
    def get_token(cls, user):
        """Add custom claims to token"""
        token = super().get_token(user)
        
        # Add custom claims
        token['email'] = user.email
        token['user_type'] = user.user_type
        token['full_name'] = user.get_full_name()
        
        return token


class UserLoginSerializer(serializers.Serializer):
    """
    Simple Login Serializer (alternative to JWT)
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate credentials"""
        email = attrs.get('email', '').lower()
        password = attrs.get('password')
        
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        
        if not user.is_verified:
            raise serializers.ValidationError(
                "Please verify your email before logging in."
            )
        
        if not user.is_active:
            raise serializers.ValidationError("Account is deactivated.")
        
        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """
    Change Password Serializer
    """
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password2 = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate passwords"""
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                "new_password": "New password fields didn't match."
            })
        return attrs
    
    def validate_old_password(self, value):
        """Check old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    User Profile Update Serializer
    """
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number',
            'profile_image', 'date_of_birth',
            'address', 'city', 'country', 'postal_code'
        ]
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        if value and not value.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise serializers.ValidationError("Invalid phone number format.")
        return value
