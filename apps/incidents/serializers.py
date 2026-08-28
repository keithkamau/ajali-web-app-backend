from rest_framework import serializers

from core.validators import validate_media_upload

from .models import Incident, IncidentMedia, IncidentStatusHistory


class IncidentMediaSerializer(serializers.ModelSerializer):
	class Meta:
		model = IncidentMedia
		fields = ("id", "media_type", "media_url", "public_id", "mime_type", "file_size_bytes", "uploaded_at")
		read_only_fields = ("id", "uploaded_at")

	def validate(self, attrs):
		validate_media_upload(media_type=attrs.get("media_type"), mime_type=attrs.get("mime_type"), file_size_bytes=attrs.get("file_size_bytes"))
		return attrs


class IncidentStatusUpdateSerializer(serializers.Serializer):
	status = serializers.ChoiceField(choices=Incident.Status.choices)
	comment = serializers.CharField(required=False, allow_blank=True, max_length=2000)


class IncidentStatusHistorySerializer(serializers.ModelSerializer):
	class Meta:
		model = IncidentStatusHistory
		fields = ("id", "old_status", "new_status", "changed_by", "comment", "changed_at")
		read_only_fields = fields


class IncidentSerializer(serializers.ModelSerializer):
	media = IncidentMediaSerializer(many=True, read_only=True)
	status_history = IncidentStatusHistorySerializer(many=True, read_only=True)

	class Meta:
		model = Incident
		fields = ("id", "user", "title", "description", "type", "location_lat", "location_lng", "location_address", "status", "is_anonymous", "created_at", "updated_at", "media", "status_history")
		read_only_fields = ("id", "user", "status", "created_at", "updated_at", "media", "status_history")
