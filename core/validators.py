"""
Custom validators for the API
"""
import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

def validate_kenyan_phone(value):
    """
    Validate Kenyan phone number format
    """
    if not value:
        return value
    
    pattern = r'^(?:\+254|0)(7|1)\d{8}$'
    if not re.match(pattern, value):
        raise ValidationError(
            'Invalid phone number format. Use +2547XXXXXXXX or 07XXXXXXXX'
        )
    return value

def validate_password_strength(password):
    """
    Validate password strength
    """
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long')
    
    if not any(c.isupper() for c in password):
        raise ValidationError('Password must contain at least one uppercase letter')
    
    if not any(c.islower() for c in password):
        raise ValidationError('Password must contain at least one lowercase letter')
    
    if not any(c.isdigit() for c in password):
        raise ValidationError('Password must contain at least one number')
    
    if not any(c in '!@#$%^&*()_+-=[]{};:\'",.<>/?\\|`~' for c in password):
        raise ValidationError('Password must contain at least one special character')
    
    return password

def validate_email_unique(email):
    """
    Validate that email is unique
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if User.objects.filter(email=email.lower()).exists():
        raise ValidationError('Email already registered')
    
    return email