from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .models import Incident, IncidentMedia
from .permissions import IsIncidentOwner
from .serializers import IncidentMediaSerializer, IncidentSerializer, IncidentStatusHistorySerializer, IncidentStatusUpdateSerializer
from .services import attach_media, change_status, create_incident, delete_media
from core.geocoding import forward_geocode, reverse_geocode
from core.cloudinary_utils import generate_upload_signature, delete_from_cloudinary, upload_to_cloudinary
class CloudinaryUploadSignatureView(generics.GenericAPIView):
	permission_classes = (permissions.IsAuthenticated, IsIncidentOwner)

	def get(self, request, pk):
		incident = get_object_or_404(Incident, pk=pk)
		self.check_object_permissions(request, incident)
		signature_data = generate_upload_signature(folder=f"ajali/incidents/{incident.id}")
		return Response(signature_data)

class ReverseGeocodeView(generics.GenericAPIView):
	permission_classes = (permissions.IsAuthenticated,)

	def get(self, request):
		lat = request.query_params.get("lat")
		lng = request.query_params.get("lng")
		if not lat or not lng:
			return Response({"detail": "lat and lng query params are required."}, status=status.HTTP_400_BAD_REQUEST)
		address = reverse_geocode(lat=lat, lng=lng)
		return Response({"address": address})


class ForwardGeocodeView(generics.GenericAPIView):
	permission_classes = (permissions.IsAuthenticated,)

	def get(self, request):
		address = request.query_params.get("address")
		if not address:
			return Response({"detail": "address query param is required."}, status=status.HTTP_400_BAD_REQUEST)
		result = forward_geocode(address=address)
		return Response(result)

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


class IncidentSearchView(IncidentListCreateView):
	http_method_names = ("get", "head", "options")


class IncidentFilterView(IncidentListCreateView):
	http_method_names = ("get", "head", "options")


class IncidentDetailView(generics.RetrieveUpdateDestroyAPIView):
	serializer_class = IncidentSerializer
	permission_classes = (permissions.IsAuthenticated, IsIncidentOwner)

	def get_queryset(self):
		# Not filtered by user here on purpose: we want DRF to find the row
		# regardless of owner, so IsIncidentOwner.has_object_permission()
		# is what rejects non-owners (403), rather than the queryset hiding
		# the row and producing a 404.
		return Incident.objects.all().prefetch_related("media", "status_history")


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
			incident = change_status(
				incident=incident,
				changed_by=request.user,
				new_status=serializer.validated_data["status"],
				comment=serializer.validated_data.get("comment", ""),
			)
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


class IncidentMediaDeleteView(generics.DestroyAPIView):
	permission_classes = (permissions.IsAuthenticated, IsIncidentOwner)

	def delete(self, request, pk, media_id):
		incident = get_object_or_404(Incident, pk=pk)
		self.check_object_permissions(request, incident)
		media = get_object_or_404(IncidentMedia, pk=media_id, incident=incident)
		delete_media(media=media)
		return Response(status=status.HTTP_204_NO_CONTENT)


class IncidentImageDeleteView(IncidentMediaDeleteView):
	pass


class IncidentVideoDeleteView(IncidentMediaDeleteView):
	pass


class PublicIncidentListView(generics.ListAPIView):
	serializer_class = IncidentSerializer
	permission_classes = (permissions.AllowAny,)
	queryset = Incident.objects.filter(is_anonymous=False).prefetch_related("media", "status_history")