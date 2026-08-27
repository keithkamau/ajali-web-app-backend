from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from rest_framework.exceptions import ValidationError

_geolocator = Nominatim(user_agent="ajali-incident-reporting-app")


def reverse_geocode(*, lat, lng):
    """
    Convert coordinates into a human-readable address.
    Returns the address string, or raises ValidationError if it fails.
    """
    try:
        location = _geolocator.reverse((lat, lng), timeout=5)
    except (GeocoderTimedOut, GeocoderServiceError) as error:
        raise ValidationError(f"Could not reach geocoding service: {error}")

    if location is None:
        raise ValidationError("No address found for these coordinates.")

    return location.address


def forward_geocode(*, address):
    """
    Convert an address into coordinates.
    Returns a dict with lat/lng, or raises ValidationError if it fails.
    """
    try:
        location = _geolocator.geocode(address, timeout=5)
    except (GeocoderTimedOut, GeocoderServiceError) as error:
        raise ValidationError(f"Could not reach geocoding service: {error}")

    if location is None:
        raise ValidationError("No coordinates found for this address.")

    return {
        "lat": str(location.latitude),
        "lng": str(location.longitude),
        "address": location.address,
    }