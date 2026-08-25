import secrets
import re
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

def generate_username_from_email(email):
    """
    Generate a username from email address
    """
    return email.split('@')[0].lower().replace('.', '_')

def validate_password_against_common(password):
    """
    Check password against common passwords list
    """
    common_passwords = [
        'password', '123456', 'password123', 'admin',
        'qwerty', 'letmein', 'welcome', 'admin123'
    ]
    
    if password.lower() in common_passwords:
        raise ValidationError('Password is too common')
    
    return password

def generate_otp():
    """
    Generate a 6-digit OTP
    """
    return f"{secrets.randbelow(900000) + 100000}"

def is_valid_uuid(uuid_string):
    """
    Validate UUID format
    """
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return re.match(pattern, str(uuid_string)) is not None

def sanitize_user_input(data):
    """
    Sanitize user input data
    """
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = value.strip()
        else:
            sanitized[key] = value
    return sanitized

def mask_email(email):
    """
    Mask email for display (e.g., u***r@example.com)
    """
    if not email:
        return email
    
    parts = email.split('@')
    if len(parts) != 2:
        return email
    
    username, domain = parts
    if len(username) <= 2:
        masked_username = username[0] + '***'
    else:
        masked_username = username[0] + '***' + username[-1]
    
    return f"{masked_username}@{domain}"

def mask_phone(phone):
    """
    Mask phone number for display
    """
    if not phone:
        return phone
    
    if len(phone) <= 4:
        return phone
    
    return phone[:4] + '***' + phone[-2:]

def get_client_ip(request):
    """
    Get client IP address from request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_user_activity(user, action, request, details=None):
    """
    Log user activity
    """
    from .models import UserActivityLog
    
    UserActivityLog.objects.create(
        user=user,
        action=action,
        details=details or {},
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

def is_strong_password(password):
    """
    Check if password is strong
    """
    if len(password) < 8:
        return False, 'Password must be at least 8 characters long'
    
    if not any(c.isupper() for c in password):
        return False, 'Password must contain at least one uppercase letter'
    
    if not any(c.islower() for c in password):
        return False, 'Password must contain at least one lowercase letter'
    
    if not any(c.isdigit() for c in password):
        return False, 'Password must contain at least one number'
    
    if not any(c in '!@#$%^&*()_+-=[]{};:\'",.<>/?\\|`~' for c in password):
        return False, 'Password must contain at least one special character'
    
    return True, 'Password is strong'