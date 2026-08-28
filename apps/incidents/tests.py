import factory
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.exceptions import ValidationError as DRFValidationError

from core.validators import MAX_IMAGE_BYTES

from .models import Incident, IncidentMedia, IncidentStatusHistory
from .services import attach_media, change_status, create_incident, delete_media
from unittest.mock import patch, MagicMock


@patch("core.geocoding._geolocator")
def test_reverse_geocode_returns_address(mock_geolocator):
	mock_location = MagicMock()
	mock_location.address = "Nairobi Expressway, Kilimani, Nairobi, Kenya"
	mock_geolocator.reverse.return_value = mock_location

	from core.geocoding import reverse_geocode
	result = reverse_geocode(lat="-1.286389", lng="36.817223")

	assert result == "Nairobi Expressway, Kilimani, Nairobi, Kenya"


@patch("core.geocoding._geolocator")
def test_forward_geocode_returns_coordinates(mock_geolocator):
	mock_location = MagicMock()
	mock_location.latitude = -1.302398
	mock_location.longitude = 36.8288509
	mock_location.address = "Nairobi, Kenya"
	mock_geolocator.geocode.return_value = mock_location

	from core.geocoding import forward_geocode
	result = forward_geocode(address="Nairobi, Kenya")

	assert result == {"lat": "-1.302398", "lng": "36.8288509", "address": "Nairobi, Kenya"}

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = User
		skip_postgeneration_save = True

	email = factory.Sequence(lambda number: f"user{number}@example.com")
	full_name = factory.Faker("name")
	password = factory.PostGenerationMethodCall("set_password", "Test@123456")


class IncidentFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = Incident
		skip_postgeneration_save = True

	user = factory.SubFactory(UserFactory)
	title = factory.Sequence(lambda number: f"Incident {number}")
	description = "A reported incident"
	type = "theft"
	location_lat = "-1.286389"
	location_lng = "36.817223"
	location_address = "Nairobi"

	@factory.post_generation
	def create_status_history(self, create, extracted, **kwargs):
		if create:
			IncidentStatusHistory.objects.create(incident=self, new_status=self.status, changed_by=self.user)


class IncidentMediaFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = IncidentMedia

	incident = factory.SubFactory(IncidentFactory)
	media_type = IncidentMedia.MediaType.IMAGE
	media_url = factory.Sequence(lambda number: f"https://cdn.example.com/{number}.jpg")
	mime_type = "image/jpeg"
	file_size_bytes = 1024


@pytest.fixture
def client():
	return APIClient()


@pytest.fixture
def owner():
	return UserFactory()


@pytest.fixture
def incident(owner):
	return IncidentFactory(user=owner)


def incident_payload(title="New incident"):
	return {
		"title": title,
		"description": "A detailed incident report",
		"type": "theft",
		"location_lat": "-1.286389",
		"location_lng": "36.817223",
		"location_address": "Nairobi",
		"is_anonymous": False,
	}


def authenticate(client, user):
	client.force_authenticate(user=user)


@pytest.mark.django_db
def test_incident_creation_and_str(owner):
	incident = IncidentFactory(user=owner, title="Broken streetlight")

	assert incident.user == owner
	assert str(incident) == "Broken streetlight"


@pytest.mark.django_db
def test_create_incident_creates_initial_status_history(owner):
	incident = create_incident(user=owner, validated_data=incident_payload())

	history = IncidentStatusHistory.objects.get(incident=incident)
	assert incident.status == Incident.Status.REPORTED
	assert history.old_status is None
	assert history.new_status == Incident.Status.REPORTED
	assert history.changed_by == owner


@pytest.mark.django_db
def test_change_status_creates_history(owner, incident):
	change_status(incident=incident, changed_by=owner, new_status=Incident.Status.IN_PROGRESS, comment="Assigned")

	incident.refresh_from_db()
	history = incident.status_history.first()
	assert incident.status == Incident.Status.IN_PROGRESS
	assert history.old_status == Incident.Status.REPORTED
	assert history.new_status == Incident.Status.IN_PROGRESS
	assert history.comment == "Assigned"


@pytest.mark.django_db
def test_change_status_rejects_same_status(owner, incident):
	with pytest.raises(ValueError, match="must differ"):
		change_status(incident=incident, changed_by=owner, new_status=incident.status)


@pytest.mark.django_db
def test_attach_media_rejects_bad_mime_type(incident):
	with pytest.raises(DRFValidationError, match="Unsupported MIME type"):
		attach_media(incident=incident, media_type="image", media_url="https://cdn.example.com/a.gif", mime_type="image/gif", file_size_bytes=1024)


@pytest.mark.django_db
def test_attach_media_rejects_oversized_file(incident):
	with pytest.raises(DRFValidationError, match="smaller than"):
		attach_media(incident=incident, media_type="image", media_url="https://cdn.example.com/a.jpg", mime_type="image/jpeg", file_size_bytes=MAX_IMAGE_BYTES + 1)


@pytest.mark.django_db
def test_list_is_scoped_to_authenticated_user(client, owner, incident):
	IncidentFactory(title="Other user's incident")
	authenticate(client, owner)

	response = client.get(reverse("incident-list-create"))

	assert response.status_code == status.HTTP_200_OK
	assert response.data["count"] == 1
	assert response.data["results"][0]["id"] == str(incident.id)


@pytest.mark.django_db
def test_create_incident_view(client, owner):
	authenticate(client, owner)

	response = client.post(reverse("incident-list-create"), incident_payload(), format="json")

	assert response.status_code == status.HTTP_201_CREATED
	assert Incident.objects.filter(user=owner, title="New incident").exists()


@pytest.mark.django_db
def test_search_and_filter_views_use_user_scoped_querysets(client, owner, incident):
	IncidentFactory(user=owner, title="Noise complaint", type="noise")
	IncidentFactory(title="Private theft")
	authenticate(client, owner)

	search_response = client.get(reverse("incident-search"), {"search": "Noise"})
	filter_response = client.get(reverse("incident-filter"), {"type": "theft"})

	assert search_response.status_code == status.HTTP_200_OK
	assert search_response.data["count"] == 1
	assert filter_response.status_code == status.HTTP_200_OK
	assert filter_response.data["count"] == 1
	assert filter_response.data["results"][0]["id"] == str(incident.id)


@pytest.mark.django_db
def test_detail_update_and_delete_views(client, owner, incident):
	authenticate(client, owner)
	detail_url = reverse("incident-detail", kwargs={"pk": incident.id})

	assert client.get(detail_url).status_code == status.HTTP_200_OK
	update_response = client.patch(detail_url, {"title": "Updated title"}, format="json")
	assert update_response.status_code == status.HTTP_200_OK
	assert update_response.data["title"] == "Updated title"
	assert client.delete(detail_url).status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_non_owner_cannot_access_detail_or_status(client, incident):
	non_owner = UserFactory()
	authenticate(client, non_owner)
	detail_url = reverse("incident-detail", kwargs={"pk": incident.id})
	status_url = reverse("incident-status-update", kwargs={"pk": incident.id})

	assert client.get(detail_url).status_code == status.HTTP_403_FORBIDDEN
	assert client.post(status_url, {"status": Incident.Status.RESOLVED}, format="json").status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_status_history_view(client, owner, incident):
	authenticate(client, owner)
	response = client.get(reverse("incident-status-history", kwargs={"pk": incident.id}))

	assert response.status_code == status.HTTP_200_OK
	assert len(response.data["results"]) == 1
	assert response.data["results"][0]["new_status"] == Incident.Status.REPORTED


@pytest.mark.django_db
def test_status_update_view(client, owner, incident):
	authenticate(client, owner)
	response = client.post(reverse("incident-status-update", kwargs={"pk": incident.id}), {"status": Incident.Status.RESOLVED}, format="json")

	assert response.status_code == status.HTTP_200_OK
	assert response.data["status"] == Incident.Status.RESOLVED
	assert incident.status_history.count() == 2


@pytest.mark.django_db
def test_public_endpoint_excludes_anonymous_incidents(client):
	IncidentFactory(is_anonymous=False, title="Public report")
	IncidentFactory(is_anonymous=True, title="Private report")

	response = client.get(reverse("public-incidents"))

	assert response.status_code == status.HTTP_200_OK
	assert response.data["count"] == 1
	assert response.data["results"][0]["title"] == "Public report"


@pytest.mark.django_db
def test_media_upload_views(client, owner, incident):
	authenticate(client, owner)
	image_response = client.post(reverse("incident-image-upload", kwargs={"pk": incident.id}), {"media_url": "https://cdn.example.com/a.jpg", "mime_type": "image/jpeg", "file_size_bytes": 1024}, format="json")
	video_response = client.post(reverse("incident-video-upload", kwargs={"pk": incident.id}), {"media_url": "https://cdn.example.com/a.mp4", "mime_type": "video/mp4", "file_size_bytes": 1024}, format="json")

	assert image_response.status_code == status.HTTP_201_CREATED
	assert video_response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
@pytest.mark.parametrize("route_name,media_type", [("incident-image-delete", IncidentMedia.MediaType.IMAGE), ("incident-video-delete", IncidentMedia.MediaType.VIDEO)])
def test_delete_media_view_returns_204(client, owner, incident, route_name, media_type):
	authenticate(client, owner)
	media = IncidentMediaFactory(incident=incident, media_type=media_type, mime_type="image/jpeg" if media_type == "image" else "video/mp4")

	response = client.delete(reverse(route_name, kwargs={"pk": incident.id, "media_id": media.id}))

	assert response.status_code == status.HTTP_204_NO_CONTENT
	assert not IncidentMedia.objects.filter(id=media.id).exists()


@pytest.mark.django_db
def test_delete_media_returns_404_when_media_belongs_to_another_incident(client, owner, incident):
	authenticate(client, owner)
	media = IncidentMediaFactory()

	response = client.delete(reverse("incident-image-delete", kwargs={"pk": incident.id, "media_id": media.id}))

	assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_non_owner_cannot_delete_media(client, incident):
	media = IncidentMediaFactory(incident=incident)
	authenticate(client, UserFactory())

	response = client.delete(reverse("incident-image-delete", kwargs={"pk": incident.id, "media_id": media.id}))

	assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_media_service_removes_media(incident):
	media = IncidentMediaFactory(incident=incident)

	delete_media(media=media)

	assert not IncidentMedia.objects.filter(id=media.id).exists()

@patch("core.cloudinary_utils.cloudinary.utils.api_sign_request")
def test_generate_upload_signature_returns_expected_shape(mock_sign):
	mock_sign.return_value = "fake-signature"

	from core.cloudinary_utils import generate_upload_signature
	result = generate_upload_signature(folder="ajali/incidents/abc123")

	assert result["signature"] == "fake-signature"
	assert result["folder"] == "ajali/incidents/abc123"
	assert "timestamp" in result
	assert "api_key" in result
	assert "cloud_name" in result