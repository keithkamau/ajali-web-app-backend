from apps.users.models import User
from rest_framework import serializers
from .models import AdminActionLog

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