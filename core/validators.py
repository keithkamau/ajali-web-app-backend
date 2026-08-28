"""
Custom validators for the API
"""
import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from rest_framework import serializers

MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_VIDEO_BYTES = 50 * 1024 * 1024
ALLOWED_MEDIA_TYPES = {
    "image": ("image/jpeg", "image/png", "image/webp"),
    "video": ("video/mp4", "video/quicktime", "video/webm"),
}


def validate_media_upload(*, media_type, mime_type, file_size_bytes):
    allowed_mime_types = ALLOWED_MEDIA_TYPES.get(media_type)
    if allowed_mime_types is None:
        raise serializers.ValidationError("Media type must be image or video.")
    if mime_type not in allowed_mime_types:
        raise serializers.ValidationError(f"Unsupported MIME type for {media_type}.")
    max_size = MAX_IMAGE_BYTES if media_type == "image" else MAX_VIDEO_BYTES
    if file_size_bytes is None or file_size_bytes <= 0 or file_size_bytes > max_size:
        raise serializers.ValidationError(f"{media_type.title()} files must be smaller than {max_size // (1024 * 1024)} MB.")

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