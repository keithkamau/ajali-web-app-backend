from apps.users.models import User
from rest_framework import serializers
from .models import AdminActionLog
from apps.incidents.models import Incident, IncidentStatusHistory

class AdminActionLogSerializer(serializers.ModelSerializer):
    admin_name = serializers.CharField(
        source="admin.full_name",
        read_only=True
    )

    admin_email = serializers.EmailField(
        source="admin.email",
        read_only=True
    )

    class Meta:
        model = AdminActionLog
        fields = [
            "id",
            "admin_name",
            "admin_email",
            "action",
            "timestamp",
            "details",
        ]
        read_only_fields = [
            "id",
            "admin_name",
            "admin_email",
            "timestamp",
        ]

class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "phone_number",
            "role",
            "is_active",
            "is_verified",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "email",
            "created_at",
            "updated_at",
        ]


class AdminUserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["role"]

    def validate_role(self, value):
        if value not in ["user", "admin"]:
            raise serializers.ValidationError(
                "Role must be either 'user' or 'admin'."
            )

        return value

class AdminIncidentSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    media = serializers.SerializerMethodField()

    class Meta:
        model = Incident
        fields = [
            "id",
            "user",
            "user_email",
            "user_name",
            "title",
            "description",
            "type",
            "location_lat",
            "location_lng",
            "location_address",
            "status",
            "is_anonymous",
            "created_at",
            "updated_at",
            "media",
        ]
        read_only_fields = [
            "id",
            "user",
            "user_email",
            "user_name",
            "created_at",
            "updated_at",
            "media",
        ]

    def get_media(self, obj):
        return [
            {
                "id": str(media.id),
                "media_type": media.media_type,
                "media_url": media.media_url,
                "public_id": media.public_id,
                "mime_type": media.mime_type,
                "file_size_bytes": media.file_size_bytes,
                "uploaded_at": media.uploaded_at,
            }
            for media in obj.media.all()
        ]

class AdminIncidentStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=Incident.Status.choices
    )
    comment = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=2000
    )

class AdminStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_email = serializers.EmailField(
        source="changed_by.email",
        read_only=True
    )

    changed_by_name = serializers.CharField(
        source="changed_by.full_name",
        read_only=True
    )

    class Meta:
        model = IncidentStatusHistory
        fields = [
            "id",
            "old_status",
            "new_status",
            "changed_by",
            "changed_by_email",
            "changed_by_name",
            "comment",
            "changed_at",
        ]
        read_only_fields = fields