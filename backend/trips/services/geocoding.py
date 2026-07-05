import requests
from django.conf import settings

from .exceptions import GeocodingError

ORS_GEOCODE_URL = "https://api.openrouteservice.org/geocode/search"


def geocode(location_text: str) -> tuple[float, float]:
    """Resolves a location string to (lat, lng) via OpenRouteService."""
    try:
        response = requests.get(
            ORS_GEOCODE_URL,
            params={
                "api_key": settings.OPENROUTESERVICE_API_KEY,
                "text": location_text,
                "size": 1,
            },
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise GeocodingError(f"Could not geocode '{location_text}': {exc}") from exc

    features = response.json().get("features", [])

    if not features:
        raise GeocodingError(f"No location found for '{location_text}'")

    lng, lat = features[0]["geometry"]["coordinates"]
    return lat, lng
