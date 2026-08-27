from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from core.permissions import IsAdminUser

from .models import AdminActionLog
from .serializers import AdminActionLogSerializer
from rest_framework import serializers

from django.db.models import Q
from django.shortcuts import get_object_or_404

from django.db import transaction
from rest_framework import status, generics
from rest_framework.generics import ListAPIView, RetrieveAPIView, RetrieveDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsAdminUser
from apps.users.models import User

from apps.incidents.models import (
    Incident,
    IncidentStatusHistory,
)
from apps.incidents.services import change_status

from .models import AdminActionLog
from .serializers import (
    AdminActionLogSerializer,
    AdminUserRoleSerializer,
    AdminUserSerializer,
    AdminIncidentSerializer,
    AdminIncidentStatusSerializer,
    AdminStatusHistorySerializer,
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

class AdminStatsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        return Response({
            "total": 0,
            "resolved": 0,
            "in_progress": 0,
            "critical": 0,
        })

class AdminIncidentListView(generics.ListAPIView):
    serializer_class = AdminIncidentSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        queryset = Incident.objects.all().select_related(
            "user"
        ).prefetch_related(
            "media",
            "status_history"
        )

        status_value = self.request.query_params.get("status")
        incident_type = self.request.query_params.get("type")
        search = self.request.query_params.get("search")

        if status_value:
            queryset = queryset.filter(status=status_value)

        if incident_type:
            queryset = queryset.filter(type=incident_type)

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(location_address__icontains=search)
                | Q(type__icontains=search)
            )

        return queryset

class AdminIncidentDetailView(generics.RetrieveAPIView):
    serializer_class = AdminIncidentSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    queryset = Incident.objects.all().select_related(
        "user"
    ).prefetch_related(
        "media",
        "status_history"
    )

class AdminIncidentStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, pk):
        incident = get_object_or_404(
            Incident,
            pk=pk
        )

        serializer = AdminIncidentStatusSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        try:
            incident = change_status(
                incident=incident,
                changed_by=request.user,
                **serializer.validated_data
            )
        except ValueError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            AdminIncidentSerializer(incident).data,
            status=status.HTTP_200_OK
        )

class AdminIncidentStatusHistoryView(generics.ListAPIView):
    serializer_class = AdminStatusHistorySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        incident = get_object_or_404(
            Incident,
            pk=self.kwargs["pk"]
        )

        return incident.status_history.select_related(
            "changed_by"
        ).all()