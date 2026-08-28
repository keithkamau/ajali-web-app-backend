import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

_USER_PASSWORD = "Test@123456"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="ian@ajali.test",
        password=_USER_PASSWORD,
        full_name="Test User",
        phone_number="0712345678",
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        email="other@ajali.test",
        password=_USER_PASSWORD,
        full_name="Other User",
    )


@pytest.fixture
def auth_client(user):
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def other_auth_client(other_user):
    client = APIClient()
    refresh = RefreshToken.for_user(other_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client
