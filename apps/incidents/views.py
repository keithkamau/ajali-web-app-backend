from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .models import Incident
from .permissions import IsIncidentOwner
from .serializers import IncidentMediaSerializer, IncidentSerializer, IncidentStatusHistorySerializer, IncidentStatusUpdateSerializer
from .services import attach_media, change_status, create_incident


class IncidentListCreateView(generics.ListCreateAPIView):
	serializer_class = IncidentSerializer
	permission_classes = (permissions.IsAuthenticated,)
	filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
	filterset_fields = ("type", "status", "is_anonymous")
	search_fields = ("title", "description", "location_address", "type")
	ordering_fields = ("created_at", "updated_at", "title", "status", "type")
	ordering = ("-created_at",)

	def get_queryset(self):
		return Incident.objects.filter(user=self.request.user).prefetch_related("media", "status_history")

	def perform_create(self, serializer):
		serializer.instance = create_incident(user=self.request.user, validated_data=serializer.validated_data)


class IncidentDetailView(generics.RetrieveUpdateDestroyAPIView):
	serializer_class = IncidentSerializer
	permission_classes = (permissions.IsAuthenticated, IsIncidentOwner)

	def get_queryset(self):
		return Incident.objects.filter(user=self.request.user).prefetch_related("media", "status_history")


class IncidentStatusHistoryView(generics.ListAPIView):
	serializer_class = IncidentStatusHistorySerializer
	permission_classes = (permissions.IsAuthenticated, IsIncidentOwner)

	def get_queryset(self):
		incident = get_object_or_404(Incident, pk=self.kwargs["pk"])
		self.check_object_permissions(self.request, incident)
		return incident.status_history.all()


class IncidentStatusUpdateView(generics.GenericAPIView):
	serializer_class = IncidentStatusUpdateSerializer
	permission_classes = (permissions.IsAuthenticated, IsIncidentOwner)

	def post(self, request, pk):
		incident = get_object_or_404(Incident, pk=pk)
		self.check_object_permissions(request, incident)
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		try:
			incident = change_status(incident=incident, changed_by=request.user, **serializer.validated_data)
		except ValueError as error:
			return Response({"detail": str(error)}, status=status.HTTP_400_BAD_REQUEST)
		return Response(IncidentSerializer(incident).data)


class IncidentMediaUploadView(generics.GenericAPIView):
	serializer_class = IncidentMediaSerializer
	permission_classes = (permissions.IsAuthenticated, IsIncidentOwner)
	forced_media_type = None

	def post(self, request, pk):
		incident = get_object_or_404(Incident, pk=pk)
		self.check_object_permissions(request, incident)
		data = request.data.copy()
		if self.forced_media_type:
			data["media_type"] = self.forced_media_type
		serializer = self.get_serializer(data=data)
		serializer.is_valid(raise_exception=True)
		media = attach_media(incident=incident, **serializer.validated_data)
		return Response(IncidentMediaSerializer(media).data, status=status.HTTP_201_CREATED)


class IncidentImageUploadView(IncidentMediaUploadView):
	forced_media_type = "image"


class IncidentVideoUploadView(IncidentMediaUploadView):
	forced_media_type = "video"


class PublicIncidentListView(generics.ListAPIView):
	serializer_class = IncidentSerializer
	permission_classes = (permissions.AllowAny,)
	queryset = Incident.objects.filter(is_anonymous=False).prefetch_related("media", "status_history")
