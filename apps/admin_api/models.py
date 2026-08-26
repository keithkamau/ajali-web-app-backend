import uuid

from django.conf import settings
from django.db import models


class AdminActionLog(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="admin_actions"
    )

    action = models.CharField(max_length=100)

    timestamp = models.DateTimeField(auto_now_add=True)

    details = models.JSONField(
        blank=True,
        null=True
    )

    class Meta:
        db_table = "admin_action_logs"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.admin.email} - {self.action}"