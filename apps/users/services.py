"""
User management services
"""
import secrets
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import PasswordResetToken

User = get_user_model()

class UserService:
    """Service class for user management"""
    
    @staticmethod
    def create_user(email, password, full_name, phone_number=None, role='user'):
        """Create a new user"""
        user = User.objects.create_user(
            email=email.lower(),
            password=password,
            full_name=full_name,
            phone_number=phone_number,
            role=role
        )
        return user
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        try:
            return User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            return None
    
    @staticmethod
    def update_user(user, data):
        """Update user profile"""
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'phone_number' in data:
            user.phone_number = data['phone_number']
        user.save()
        return user
    
    @staticmethod
    def change_password(user, current_password, new_password):
        """Change user password"""
        if not user.check_password(current_password):
            raise ValueError('Current password is incorrect')
        user.set_password(new_password)
        user.save()
    
    @staticmethod
    def generate_reset_token(user):
        """Generate password reset token"""
        # Delete existing tokens
        PasswordResetToken.objects.filter(user=user).delete()
        
        # Create new token
        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=1)
        reset_token = PasswordResetToken.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        return token
    
    @staticmethod
    def reset_password(token, new_password):
        """Reset password using token"""
        reset_token = PasswordResetToken.objects.filter(token=token).first()
        
        if not reset_token:
            raise ValueError('Invalid reset token')
        
        if not reset_token.is_valid():
            raise ValueError('Reset token expired or already used')
        
        user = reset_token.user
        user.set_password(new_password)
        user.save()
        reset_token.mark_used()
    
    @staticmethod
    def send_reset_email(user, token):
        """Send password reset email"""
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{token}"
        
        subject = 'Reset Your Ajali! Password'
        message = f"""
        Hello {user.full_name},
        
        You requested to reset your password for your Ajali! account.
        
        Click the link below to reset your password:
        {reset_link}
        
        This link will expire in 1 hour.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        Ajali! Team
        """
        
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])