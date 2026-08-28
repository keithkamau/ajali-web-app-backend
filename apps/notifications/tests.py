from unittest.mock import MagicMock, patch

import pytest
from django.urls import reverse
from rest_framework import status

from apps.notifications.models import Notification, NotificationPreference
from apps.notifications.services import (
    create_notification,
    notify_incident_created,
    send_email,
    send_sms,
)


@pytest.fixture
def notification(user, db):
    return Notification.objects.create(
        user=user,
        type="incident_created",
        title="Test Notification",
        message="Test message",
    )


# ---------------------------------------------------------------------------
# List view
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestNotificationList:
    def test_returns_only_own_notifications(self, auth_client, user, other_user, db):
        Notification.objects.create(user=user, type="t", title="Mine", message="m")
        Notification.objects.create(user=other_user, type="t", title="Not mine", message="m")
        resp = auth_client.get(reverse("notification-list"))
        assert resp.status_code == status.HTTP_200_OK
        titles = [n["title"] for n in resp.data["results"]]
        assert "Mine" in titles
        assert "Not mine" not in titles

    def test_sorted_newest_first(self, auth_client, user, db):
        Notification.objects.create(user=user, type="t", title="First", message="m")
        Notification.objects.create(user=user, type="t", title="Second", message="m")
        resp = auth_client.get(reverse("notification-list"))
        titles = [n["title"] for n in resp.data["results"]]
        assert titles.index("Second") < titles.index("First")

    def test_filter_unread(self, auth_client, user, db):
        Notification.objects.create(user=user, type="t", title="Read", message="m", read=True)
        Notification.objects.create(user=user, type="t", title="Unread", message="m", read=False)
        resp = auth_client.get(reverse("notification-list") + "?unread=true")
        titles = [n["title"] for n in resp.data["results"]]
        assert "Unread" in titles
        assert "Read" not in titles

    def test_pagination_page_size(self, auth_client, user, db):
        for i in range(5):
            Notification.objects.create(user=user, type="t", title=f"N{i}", message="m")
        resp = auth_client.get(reverse("notification-list") + "?page_size=2")
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data["results"]) == 2
        assert resp.data["count"] == 5
        assert resp.data["total_pages"] == 3

    def test_requires_auth(self, api_client):
        resp = api_client.get(reverse("notification-list"))
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Unread count
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestUnreadCount:
    def test_counts_only_unread(self, auth_client, user, db):
        Notification.objects.create(user=user, type="t", title="T", message="m", read=False)
        Notification.objects.create(user=user, type="t", title="T", message="m", read=True)
        resp = auth_client.get(reverse("unread-count"))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["unread_count"] == 1


# ---------------------------------------------------------------------------
# Mark read
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestMarkRead:
    def test_marks_own_notification_read(self, auth_client, notification):
        url = reverse("notification-read", kwargs={"pk": notification.id})
        resp = auth_client.patch(url)
        assert resp.status_code == status.HTTP_200_OK
        notification.refresh_from_db()
        assert notification.read is True

    def test_cannot_mark_other_users_notification(self, other_auth_client, notification):
        url = reverse("notification-read", kwargs={"pk": notification.id})
        resp = other_auth_client.patch(url)
        assert resp.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# Mark all read
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestMarkAllRead:
    def test_marks_all_unread_as_read(self, auth_client, user, db):
        for _ in range(3):
            Notification.objects.create(user=user, type="t", title="T", message="m")
        resp = auth_client.post(reverse("notifications-read-all"))
        assert resp.status_code == status.HTTP_200_OK
        assert Notification.objects.filter(user=user, read=False).count() == 0


# ---------------------------------------------------------------------------
# Preferences
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestPreferences:
    def test_get_auto_creates_defaults(self, auth_client, user, db):
        assert not NotificationPreference.objects.filter(user=user).exists()
        resp = auth_client.get(reverse("notification-preferences"))
        assert resp.status_code == status.HTTP_200_OK
        assert NotificationPreference.objects.filter(user=user).exists()
        assert resp.data["email_enabled"] is True
        assert resp.data["sms_enabled"] is True

    def test_update_preferences(self, auth_client, user, db):
        resp = auth_client.put(
            reverse("notification-preferences"),
            {"email_enabled": False, "sms_enabled": False, "push_enabled": False},
        )
        assert resp.status_code == status.HTTP_200_OK
        pref = NotificationPreference.objects.get(user=user)
        assert pref.email_enabled is False
        assert pref.sms_enabled is False


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestDeleteNotification:
    def test_deletes_own_notification(self, auth_client, notification):
        url = reverse("notification-delete", kwargs={"pk": notification.id})
        resp = auth_client.delete(url)
        assert resp.status_code == status.HTTP_200_OK
        assert not Notification.objects.filter(id=notification.id).exists()

    def test_cannot_delete_other_users_notification(self, other_auth_client, notification):
        url = reverse("notification-delete", kwargs={"pk": notification.id})
        resp = other_auth_client.delete(url)
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_all(self, auth_client, user, other_user, db):
        for _ in range(3):
            Notification.objects.create(user=user, type="t", title="T", message="m")
        Notification.objects.create(user=other_user, type="t", title="Other", message="m")
        resp = auth_client.delete(reverse("notifications-delete-all"))
        assert resp.status_code == status.HTTP_200_OK
        assert Notification.objects.filter(user=user).count() == 0
        assert Notification.objects.filter(user=other_user).count() == 1


# ---------------------------------------------------------------------------
# Service layer
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestNotificationService:
    def test_create_notification_defaults(self, user, db):
        n = create_notification(user, "test_type", "Test Title", "Test message")
        assert n.id is not None
        assert n.user == user
        assert n.type == "test_type"
        assert n.title == "Test Title"
        assert n.read is False

    def test_send_email_skips_without_api_key(self, user, settings, db):
        settings.SENDGRID_API_KEY = ""
        result = send_email(user, "Subject", "<p>Body</p>")
        assert result is False

    def test_send_email_calls_sendgrid_when_key_present(self, user, settings, db):
        settings.SENDGRID_API_KEY = "test-key"
        with patch("apps.notifications.services.SendGridAPIClient") as mock_sg:
            mock_sg.return_value.send.return_value = MagicMock()
            result = send_email(user, "Subject", "<p>Body</p>")
        assert result is True

    def test_send_sms_skips_without_api_key(self, user, settings, db):
        settings.AFRICASTALKING_API_KEY = ""
        result = send_sms(user, "Test SMS")
        assert result is False

    def test_send_sms_skips_without_phone_number(self, user, settings, db):
        settings.AFRICASTALKING_API_KEY = "test-key"
        user.phone_number = None
        user.save()
        result = send_sms(user, "Test SMS")
        assert result is False

    def test_notify_incident_created_stores_notification(self, user, db):
        with patch("apps.notifications.services.send_email", return_value=True):
            incident = MagicMock()
            incident.title = "Test Incident"
            n = notify_incident_created(incident, user)
        assert n.id is not None
        assert Notification.objects.filter(user=user, type="incident_created").exists()

    def test_notify_incident_created_skips_email_when_disabled(self, user, db):
        NotificationPreference.objects.create(user=user, email_enabled=False)
        with patch("apps.notifications.services.send_email") as mock_email:
            incident = MagicMock()
            incident.title = "Test Incident"
            notify_incident_created(incident, user)
        mock_email.assert_not_called()
