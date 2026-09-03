import uuid
from django.conf import settings
from django.db import models


class Incident(models.Model):
    class Type(models.TextChoices):
        ACCIDENT = "accident", "Accident"
        EMERGENCY = "emergency", "Emergency"

    class Status(models.TextChoices):
        REPORTED = "reported", "Reported"
        UNDER_REVIEW = "under_review", "Under review"
        IN_PROGRESS = "in_progress", "In progress"
        RESOLVED = "resolved", "Resolved"
        REJECTED = "rejected", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="incidents")
    title = models.CharField(max_length=120)
    description = models.TextField()
    type = models.CharField(max_length=40, choices=Type.choices)  # ✅ Add choices
    location_lat = models.DecimalField(max_digits=9, decimal_places=6)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6)
    location_address = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REPORTED)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("user", "-created_at")),
            models.Index(fields=("status", "-created_at")),
            models.Index(fields=("type",)),
        ]

    def __str__(self):
        return self.title