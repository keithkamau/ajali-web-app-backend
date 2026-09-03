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
    type = models.CharField(max_length=40, choices=Type.choices)
    location_lat = models.DecimalField(max_digits=10, decimal_places=7)
    location_lng = models.DecimalField(max_digits=11, decimal_places=7)
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


class IncidentMedia(models.Model):
    class MediaType(models.TextChoices):
        IMAGE = "image", "Image"
        VIDEO = "video", "Video"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name="media")
    media_type = models.CharField(max_length=10, choices=MediaType.choices)
    media_url = models.URLField(max_length=500)
    public_id = models.CharField(max_length=255, blank=True)
    mime_type = models.CharField(max_length=100)
    file_size_bytes = models.PositiveBigIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-uploaded_at",)
        indexes = [
            models.Index(fields=("incident",)),
            models.Index(fields=("media_type",)),
        ]

    def __str__(self):
        return f"{self.incident.title} - {self.media_type}"


class IncidentStatusHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name="status_history")
    old_status = models.CharField(max_length=20, choices=Incident.Status.choices, null=True, blank=True)
    new_status = models.CharField(max_length=20, choices=Incident.Status.choices)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="incident_status_changes")
    comment = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    sequence = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        ordering = ("-sequence", "-changed_at")
        indexes = [
            models.Index(fields=("incident",)),
            models.Index(fields=("-sequence", "-changed_at")),
        ]

    def __str__(self):
        return f"{self.incident.title} - {self.old_status} → {self.new_status}"