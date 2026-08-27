"""
Custom validators for user management
"""
import re
from django.core.exceptions import ValidationError

def validate_kenyan_phone(value):
    """Validate Kenyan phone number format"""
    if not value:
        return value
    
    # Remove any whitespace
    value = value.strip()
    
    # Pattern: +254XXXXXXXX or 07XXXXXXXX or 01XXXXXXXX
    pattern = r'^(?:\+254|0)(7|1)\d{8}$'
    
    if not re.match(pattern, value):
        raise ValidationError(
            'Invalid phone number format. Use +2547XXXXXXXX, 07XXXXXXXX, or 01XXXXXXXX'
        )
    
    return value

def validate_password_strength(password):
    """Validate password strength"""
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

def validate_email_unique(value):
    """Validate email uniqueness"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    value = value.lower().strip()
    if User.objects.filter(email=value).exists():
        raise ValidationError('A user with this email already exists')
    
    return value