from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from core.permissions import IsAdminUser

from .models import AdminActionLog
from .serializers import AdminActionLogSerializer
from rest_framework import serializers

from django.db import transaction
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, RetrieveDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsAdminUser
from apps.users.models import User

from .models import AdminActionLog
from .serializers import (
    AdminActionLogSerializer,
    AdminUserRoleSerializer,
    AdminUserSerializer,
)

class AdminActionLogListView(ListAPIView):
    queryset = AdminActionLog.objects.select_related("admin")
    serializer_class = AdminActionLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class AdminUserDetailView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    lookup_field = "id"
    lookup_url_kwarg = "id"

class AdminUserRoleUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.id == request.user.id:
            return Response(
                {"detail": "You cannot change your own role."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AdminUserRoleSerializer(
            user,
            data=request.data,
            partial=False,
        )

        serializer.is_valid(raise_exception=True)

        old_role = user.role

        with transaction.atomic():
            serializer.save()

            AdminActionLog.objects.create(
                admin=request.user,
                action="update_user_role",
                details={
                    "user_id": str(user.id),
                    "old_role": old_role,
                    "new_role": user.role,
                },
            )

        return Response(
            AdminUserSerializer(user).data,
            status=status.HTTP_200_OK,
        )
    
class AdminUserDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.id == request.user.id:
            return Response(
                {"detail": "You cannot deactivate your own account."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = False
        user.save(update_fields=["is_active", "updated_at"])

        AdminActionLog.objects.create(
            admin=request.user,
            action="deactivate_user",
            details={
                "user_id": str(user.id),
                "email": user.email,
            },
        )

        return Response(
            {"detail": "User has been deactivated."},
            status=status.HTTP_200_OK,
        )

class AdminUserDetailView(RetrieveDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    lookup_field = "id"
    lookup_url_kwarg = "id"

    def perform_destroy(self, instance):
        if instance.id == self.request.user.id:
            raise serializers.ValidationError(
                "You cannot deactivate your own account."
            )

        instance.is_active = False
        instance.save(update_fields=["is_active", "updated_at"])

        AdminActionLog.objects.create(
            admin=self.request.user,
            action="deactivate_user",
            details={
                "user_id": str(instance.id),
                "email": instance.email,
            },
        )