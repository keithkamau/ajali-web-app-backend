from django.db import transaction
from core.validators import validate_media_upload
from .models import Incident, IncidentMedia, IncidentStatusHistory


@transaction.atomic
def create_incident(*, user, validated_data):
    if 'status' not in validated_data:
        validated_data['status'] = Incident.Status.REPORTED
    
    incident = Incident.objects.create(user=user, **validated_data)
    
    IncidentStatusHistory.objects.create(
        incident=incident,
        old_status=None,
        new_status=incident.status,
        changed_by=user,
        sequence=1,
        comment="Incident reported"
    )
    return incident


@transaction.atomic
def change_status(*, incident, changed_by, new_status, comment=""):
    if new_status == incident.status:
        raise ValueError("The new status must differ from the current status.")
    
    old_status = incident.status
    incident.status = new_status
    incident.save(update_fields=("status", "updated_at"))
    
    next_sequence = incident.status_history.count() + 1
    
    IncidentStatusHistory.objects.create(
        incident=incident,
        old_status=old_status,
        new_status=new_status,
        changed_by=changed_by,
        comment=comment or f"Status changed from {old_status} to {new_status}",
        sequence=next_sequence
    )
    return incident


def attach_media(*, incident, media_type, media_url, mime_type, file_size_bytes, public_id=""):
    validate_media_upload(media_type=media_type, mime_type=mime_type, file_size_bytes=file_size_bytes)
    return IncidentMedia.objects.create(
        incident=incident,
        media_type=media_type,
        media_url=media_url,
        mime_type=mime_type,
        file_size_bytes=file_size_bytes,
        public_id=public_id
    )


def delete_media(*, media):
    media.delete()