from rest_framework import viewsets
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.core.mail import EmailMultiAlternatives
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework import status, viewsets, serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import logout
from . import models
from . import utils
from . import serializers

class CustomerViewset(viewsets.ModelViewSet):
    queryset = models.Customer.objects.all()
    serializer_class = serializers.CustomerSerializer


class RegisteredUsersCount(APIView):
   
    def get(self, request):
        users_count = User.objects.count()  # Count all users in the database
        return Response({"registered_users": users_count})




class UserRegistrationAPIView(APIView):
    serializer_class = serializers.RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False 
            user.save()

            profile, created = models.CustomUser.objects.get_or_create(user=user)
            profile.otp = utils.generate_otp()  
            profile.save()

            email_subject = 'Welcome To Our Platform!'
            email_body = render_to_string('welcome_email.html', {'username': user.username})

            email = EmailMultiAlternatives(email_subject, '', 'mdmamun340921@gmail.com', [user.email])
            email.attach_alternative(email_body, 'text/html')
            email.send()

            return Response({'detail': 'Check your email for confirmation'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendOTPApiView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        user = get_object_or_404(User, email=email)

        otp_code = utils.generate_otp()
        user.profile.otp = otp_code
        user.profile.save()

        send_mail(
            'Your OTP Code : ',
            f'Your New OTP Code Is : {otp_code}',
            'mdmamun340921@gmail.com',
            [email]
        )

        return Response({'Message' : 'OTP Has Been Resent To Your Email'}, status=status.HTTP_200_OK)

class VerifyOTPApiView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        otp = request.data.get('otp')

        user = get_object_or_404(User, email=email)
        profile = user.profile

        if profile.otp == otp:
            user.is_active = True
            user.save(update_fields=['is_active']) 
            profile.otp = None
            profile.save(update_fields=['otp']) 
            return Response({'Message' : 'Account Activate Successfully'}, status=status.HTTP_200_OK)
        return Response({'Error' : 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

class UserLoginApiView(APIView):
    serializer_class = serializers.LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)

            if user:
                login(request, user)
                serializer = serializers.UserLoginSerializer({
                    'username': user.username
                })
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)




class UserLogoutApiView(APIView):
    authentication_classes = [TokenAuthentication]  # Require token authentication
    permission_classes = [IsAuthenticated]  # Only authenticated users can logout

    def post(self, request):
        user = request.user
        if hasattr(user, 'auth_token'):
            user.auth_token.delete()  # Delete the authentication token
        
        logout(request)  # Log out the user (if session-based authentication is used)

        return Response({"message": "Logout successful"}, status=status.HTTP_204_NO_CONTENT)


class ChangePasswordViewSet(viewsets.GenericViewSet):
    serializer_class = serializers.ChangePasswordSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  # ✅ শুধুমাত্র অথেনটিকেটেড ইউজার অনুমতি পাবে

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:  # ✅ অ্যানোনিমাস ইউজার চেক করা
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

        user = request.user
        serializer = self.get_serializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            if not user.check_password(serializer.validated_data["old_password"]):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response({"message": "Password changed successfully!"}, status=status.HTTP_204_NO_CONTENT)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):

    def get(self, request):
        user = request.user
        serializer = serializers.CustomUserSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user 
        serializer = serializers.CustomUserSerializer(user, data=request.data, partial=True)  # partial=True allows partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

from rest_framework import viewsets
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

User = get_user_model()

from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import UserSerializer

class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    
class IsAdminStatusAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request, *args, **kwargs):

        if request.user.is_staff:
            return Response({"is_admin": True})
        return Response({"is_admin": False})


