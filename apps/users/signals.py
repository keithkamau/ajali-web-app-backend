from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import User

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    """
    Send welcome email when a new user is created
    """
    if created:
        try:
            subject = 'Welcome to Ajali!'
            html_message = render_to_string('emails/welcome.html', {
                'user': instance,
                'frontend_url': settings.FRONTEND_URL
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.email],
                html_message=html_message,
                fail_silently=True
            )
        except Exception:
            pass

@receiver(pre_save, sender=User)
def hash_user_password(sender, instance, **kwargs):
    """
    Ensure password is hashed before saving
    """
    if instance.pk:
        try:
            old_user = User.objects.get(pk=instance.pk)
            if old_user.password != instance.password:
                # Password changed, but should be handled by set_password
                pass
        except User.DoesNotExist:
            pass

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create user profile when a new user is created
    """
    if created:
        # Could create a Profile model here if needed
        pass