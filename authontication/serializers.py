from rest_framework import serializers
from . import models
from .utils import generate_otp
from django.contrib.auth.models import User
from django.contrib.auth import password_validation
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Customer
        fields = '__all__'

class RegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'confirm_password', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        user.is_active = False 
        user.save()

        otp_code = generate_otp()
        models.CustomUser.objects.create(user=user, otp=otp_code)

        email_subject = 'Your OTP Code : '
        email_body = f'Your OTP Code Is : {otp_code}'
        send_mail(
            email_subject,
            email_body,
            'mdmamun340921@gmail.com', 
            [user.email]
        )
        
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class UserLoginSerializer(serializers.ModelSerializer):
    tokens = serializers.SerializerMethodField()
    
    def get_tokens(self, obj):
        user = User.objects.get(username=obj['username'])
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    
    class Meta:
        model = User
        fields = ['username', 'tokens']

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate_new_password(self, value):
        password_validation.validate_password(value, self.context['request'].user)
        return value

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "New password and confirm password do not match."})
        return data



from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # ব্রাউজেবল API তে সব ফিল্ড দেখানোর জন্য
        representation['id'] = instance.id
        representation['username'] = instance.username
        representation['first_name'] = instance.first_name
        representation['last_name'] = instance.last_name
        representation['email'] = instance.email
        return representation

# serializers.py
from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'