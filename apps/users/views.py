from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings

from .models import User, PasswordResetToken
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    ChangePasswordSerializer, ForgotPasswordSerializer,
    ResetPasswordSerializer
)
from core.permissions import IsAdminUser
from core.utils import generate_reset_token, get_expiry_time

class RegisterView(generics.CreateAPIView):
    """
    Register a new user
    POST /api/auth/register/
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

class LoginView(APIView):
    """
    Login user and return tokens
    POST /api/auth/login/
    """
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        user = authenticate(email=email, password=password)
        
        if not user:
            return Response(
                {'error': 'Invalid email or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return Response(
                {'error': 'Account is deactivated'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Login successful',
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user': UserSerializer(user).data
        })

class LogoutView(APIView):
    """
    Logout user
    POST /api/auth/logout/
    """
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass
        return Response({'message': 'Logout successful'})

class RefreshTokenView(TokenRefreshView):
    """
    Refresh access token
    POST /api/auth/refresh/
    """
    pass

class CurrentUserView(generics.RetrieveUpdateAPIView):
    """
    Get and update current user profile
    GET /api/auth/me/
    PUT /api/auth/me/
    """
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_object(self):
        return self.request.user

class ChangePasswordView(APIView):
    """
    Change user password
    POST /api/auth/change-password/
    """
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        if not user.check_password(serializer.validated_data['current_password']):
            return Response(
                {'error': 'Current password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'message': 'Password changed successfully'})

class ForgotPasswordView(APIView):
    """
    Request password reset
    POST /api/auth/forgot-password/
    """
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()
        
        if not user:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Delete existing tokens
        PasswordResetToken.objects.filter(user=user).delete()
        
        # Create new token
        token = generate_reset_token()
        expires_at = get_expiry_time(hours=1)
        PasswordResetToken.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        
        # Send email
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{token}"
        
        subject = 'Password Reset Request'
        message = f"""
        Hello {user.full_name},
        
        You requested to reset your password. Click the link below to reset your password:
        
        {reset_link}
        
        This link will expire in 1 hour.
        
        If you did not request this, please ignore this email.
        
        Best regards,
        Ajali! Team
        """
        
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        
        return Response({'message': 'Password reset email sent'})

class ResetPasswordView(APIView):
    """
    Reset password with token
    POST /api/auth/reset-password/
    """
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        reset_token = PasswordResetToken.objects.filter(token=token).first()
        
        if not reset_token:
            return Response(
                {'error': 'Invalid reset token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not reset_token.is_valid():
            return Response(
                {'error': 'Reset token expired or already used'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = reset_token.user
        user.set_password(new_password)
        user.save()
        
        reset_token.mark_used()
        
        return Response({'message': 'Password reset successful'})