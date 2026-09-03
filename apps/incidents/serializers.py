from rest_framework import serializers
from .models import Incident, IncidentMedia, IncidentStatusHistory


class IncidentMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentMedia
        fields = ['id', 'incident', 'media_type', 'media_url', 'public_id', 'mime_type', 'file_size_bytes', 'uploaded_at']
        read_only_fields = ['id', 'incident', 'uploaded_at']


class IncidentStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentStatusHistory
        fields = ['id', 'incident', 'old_status', 'new_status', 'changed_by', 'comment', 'changed_at', 'sequence']
        read_only_fields = ['id', 'incident', 'changed_by', 'changed_at', 'sequence']


class IncidentSerializer(serializers.ModelSerializer):
    media = IncidentMediaSerializer(many=True, read_only=True)
    status_history = IncidentStatusHistorySerializer(many=True, read_only=True)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Incident
        fields = [
            'id', 'title', 'description', 'type', 'status',
            'location_lat', 'location_lng', 'location_address',
            'user', 'user_name', 'is_anonymous',
            'media', 'status_history',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'status', 'created_at', 'updated_at']
        extra_kwargs = {
            'location_lat': {
                'required': True,
                'allow_null': False,
                'coerce_to_string': False,
            },
            'location_lng': {
                'required': True,
                'allow_null': False,
                'coerce_to_string': False,
            },
        }

    def get_user_name(self, obj):
        if obj.is_anonymous:
            return "Anonymous"
        return obj.user.full_name if obj.user else "Unknown"

    def validate_location_lat(self, value):
        """Validate latitude is within valid range"""
        if value is None:
            raise serializers.ValidationError("Latitude is required")
        if value < -90 or value > 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90")
        return value

    def validate_location_lng(self, value):
        """Validate longitude is within valid range"""
        if value is None:
            raise serializers.ValidationError("Longitude is required")
        if value < -180 or value > 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180")
        return value


class IncidentStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Incident.Status.choices)
    comment = serializers.CharField(required=False, allow_blank=True, max_length=500)