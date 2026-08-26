import uuid

from django.conf import settings
from django.db import models


class Notification(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
	type = models.CharField(max_length=50)
	title = models.CharField(max_length=255)
	message = models.TextField()
	read = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ("-created_at",)


class NotificationPreference(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notification_preferences")
	email_enabled = models.BooleanField(default=True)
	sms_enabled = models.BooleanField(default=True)
	push_enabled = models.BooleanField(default=True)
