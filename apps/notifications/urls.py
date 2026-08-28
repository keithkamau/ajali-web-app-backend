from django.urls import path

from . import views

urlpatterns = [
    path("", views.NotificationListView.as_view(), name="notification-list"),
    path("read-all/", views.MarkAllNotificationsReadView.as_view(), name="notifications-read-all"),
    path("unread-count/", views.UnreadNotificationCountView.as_view(), name="unread-count"),
    path("preferences/", views.NotificationPreferencesView.as_view(), name="notification-preferences"),
    path("all/", views.DeleteAllNotificationsView.as_view(), name="notifications-delete-all"),
    path("<uuid:pk>/read/", views.MarkNotificationReadView.as_view(), name="notification-read"),
    path("<uuid:pk>/", views.DeleteNotificationView.as_view(), name="notification-delete"),
]
