from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from apps.incidents.models import Incident
from apps.incidents.serializers import IncidentSerializer
from apps.incidents.services import change_status
from core.permissions import IsAdminUser


class AdminIncidentListView(generics.ListAPIView):
    """List all incidents (Admin only)"""
    serializer_class = IncidentSerializer
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        queryset = Incident.objects.all().prefetch_related("media", "status_history")
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        type_filter = self.request.query_params.get('type')
        if type_filter:
            queryset = queryset.filter(type=type_filter)
        
        return queryset


class AdminIncidentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete any incident (Admin only)"""
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    permission_classes = (IsAdminUser,)
    lookup_field = 'id'


class AdminIncidentStatusUpdateView(APIView):
    """Update incident status (Admin only)"""
    permission_classes = (IsAdminUser,)

    def put(self, request, id):
        incident = get_object_or_404(Incident, id=id)
        
        status_value = request.data.get('status')
        comment = request.data.get('comment', '')
        
        status_mapping = {
            'under_investigation': 'under_review',
            'reported': 'reported',
            'under_review': 'under_review',
            'in_progress': 'in_progress',
            'resolved': 'resolved',
            'rejected': 'rejected',
            'pending': 'reported',
        }
        
        if status_value in status_mapping:
            status_value = status_mapping[status_value]
        
        valid_statuses = [choice[0] for choice in Incident.Status.choices]
        if status_value not in valid_statuses:
            return Response(
                {"status": [f"'{status_value}' is not a valid choice. Valid choices: {valid_statuses}"]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            incident = change_status(
                incident=incident,
                changed_by=request.user,
                new_status=status_value,
                comment=comment
            )
        except ValueError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = IncidentSerializer(incident)
        return Response(serializer.data)


class AdminIncidentStatusUpdateView(APIView):
    permission_classes = (IsAdminUser,)

    def put(self, request, id):
        incident = get_object_or_404(Incident, id=id)
        
        status_value = request.data.get('status')
        comment = request.data.get('comment', '')
        
        status_mapping = {
            'under_investigation': 'under_review',
            'reported': 'reported',
            'under_review': 'under_review',
            'in_progress': 'in_progress',
            'resolved': 'resolved',
            'rejected': 'rejected',
            'pending': 'reported',
        }
        
        if status_value in status_mapping:
            status_value = status_mapping[status_value]
        
        valid_statuses = [choice[0] for choice in Incident.Status.choices]
        if status_value not in valid_statuses:
            return Response(
                {"status": [f"'{status_value}' is not a valid choice."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            incident = change_status(
                incident=incident,
                changed_by=request.user,
                new_status=status_value,
                comment=comment
            )
        except ValueError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = IncidentSerializer(incident)
        return Response(serializer.data)