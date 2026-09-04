from rest_framework import serializers
from decimal import Decimal
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
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Incident
        fields = [
            'id', 'title', 'description', 'type', 'status', 'status_display',
            'location_lat', 'location_lng', 'location_address',
            'user', 'user_name', 'is_anonymous',
            'media', 'status_history',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'status', 'created_at', 'updated_at']

    def get_status_display(self, obj):
        return dict(Incident.Status.choices).get(obj.status, obj.status)

    def get_user_name(self, obj):
        if obj.is_anonymous:
            return "Anonymous"
        return obj.user.full_name if obj.user else "Unknown"

    def validate_location_lat(self, value):
        """Validate latitude is within valid range - no digit limit validation"""
        if value is None:
            raise serializers.ValidationError("Latitude is required")
        
        # Convert to Decimal if needed
        if not isinstance(value, Decimal):
            try:
                value = Decimal(str(value))
            except:
                raise serializers.ValidationError("Invalid latitude format")
        
        # Only validate range, not digit count
        if value < Decimal('-90') or value > Decimal('90'):
            raise serializers.ValidationError("Latitude must be between -90 and 90")
        
        return value

    def validate_location_lng(self, value):
        """Validate longitude is within valid range - no digit limit validation"""
        if value is None:
            raise serializers.ValidationError("Longitude is required")
        
        # Convert to Decimal if needed
        if not isinstance(value, Decimal):
            try:
                value = Decimal(str(value))
            except:
                raise serializers.ValidationError("Invalid longitude format")
        
        if value < Decimal('-180') or value > Decimal('180'):
            raise serializers.ValidationError("Longitude must be between -180 and 180")
        
        return value

    def validate(self, data):
        """Additional cross-field validation if needed"""
        if 'location_lat' not in data or data['location_lat'] is None:
            raise serializers.ValidationError({"location_lat": "Latitude is required"})
        if 'location_lng' not in data or data['location_lng'] is None:
            raise serializers.ValidationError({"location_lng": "Longitude is required"})
        return data


class IncidentStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Incident.Status.choices)
    comment = serializers.CharField(required=False, allow_blank=True, max_length=500)