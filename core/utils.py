"""
Utility functions for the API
"""
import secrets
import re
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import cloudinary.uploader

def generate_reset_token():
    """
    Generate a secure reset token
    """
    return secrets.token_urlsafe(32)

def get_expiry_time(hours=1):
    """
    Get expiration time for reset token
    """
    return timezone.now() + timedelta(hours=hours)

def format_response(data, message=None):
    """
    Format API response
    """
    response = {'data': data}
    if message:
        response['message'] = message
    return response

def upload_to_cloudinary(file, folder='ajali'):
    """
    Upload file to Cloudinary
    """
    try:
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type='auto'
        )
        return {
            'url': result['secure_url'],
            'public_id': result['public_id'],
            'format': result.get('format'),
            'size': result.get('bytes')
        }
    except Exception as e:
        raise ValueError(f'File upload failed: {str(e)}')

def send_email_notification(to_email, subject, template, context):
    """
    Send email notification using SendGrid or SMTP
    """
    # Implementation using SendGrid or SMTP
    pass

def send_sms_notification(phone_number, message):
    """
    Send SMS notification using Africa's Talking
    """
    # Implementation using Africa's Talking API
    pass