from django.db import models
from django.conf import settings
import uuid

class AdminActionLog(models.Model):
    """Log of admin actions for audit trail"""
    
    class Meta:
        app_label = 'admin_api'  # ✅ Add this
        db_table = 'admin_action_logs'
        ordering = ['-created_at']
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_actions')
    action = models.CharField(max_length=100)
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.admin.email} - {self.action} - {self.created_at}"