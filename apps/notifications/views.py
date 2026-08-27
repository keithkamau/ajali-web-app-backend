from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import Notification, NotificationPreference
from .serializers import NotificationPreferenceSerializer, NotificationSerializer


class NotificationListView(generics.ListAPIView):
	serializer_class = NotificationSerializer
	permission_classes = (permissions.IsAuthenticated,)

	def get_queryset(self):
		return Notification.objects.filter(user=self.request.user)


class MarkNotificationReadView(generics.UpdateAPIView):
	serializer_class = NotificationSerializer
	permission_classes = (permissions.IsAuthenticated,)
	http_method_names = ("patch", "put", "options", "head")

	def get_queryset(self):
		return Notification.objects.filter(user=self.request.user)

	def update(self, request, *args, **kwargs):
		notification = self.get_object()
		notification.read = True
		notification.save(update_fields=("read",))
		return Response(NotificationSerializer(notification).data)


class MarkAllNotificationsReadView(generics.GenericAPIView):
	permission_classes = (permissions.IsAuthenticated,)

	def post(self, request):
		Notification.objects.filter(user=request.user, read=False).update(read=True)
		return Response({"message": "Notifications marked as read."})


class UnreadNotificationCountView(generics.GenericAPIView):
	permission_classes = (permissions.IsAuthenticated,)

	def get(self, request):
		count = Notification.objects.filter(user=request.user, read=False).count()
		return Response({"count": count})


class NotificationPreferencesView(generics.RetrieveUpdateAPIView):
	serializer_class = NotificationPreferenceSerializer
	permission_classes = (permissions.IsAuthenticated,)

	def get_object(self):
		preference, _ = NotificationPreference.objects.get_or_create(user=self.request.user)
		return preference
