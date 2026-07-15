import requests
from django.conf import settings

from .exceptions import GeocodingError

ORS_GEOCODE_URL = "https://api.openrouteservice.org/geocode/search"
ORS_AUTOCOMPLETE_URL = "https://api.openrouteservice.org/geocode/autocomplete"


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


def autocomplete(query_text: str, limit: int = 5) -> list[dict]:
    """Returns up to `limit` place suggestions for a partial location string."""
    try:
        response = requests.get(
            ORS_AUTOCOMPLETE_URL,
            params={
                "api_key": settings.OPENROUTESERVICE_API_KEY,
                "text": query_text,
                "size": limit,
            },
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise GeocodingError(f"Could not fetch suggestions for '{query_text}': {exc}") from exc

    features = response.json().get("features", [])
    return [
        {
            "label": feature["properties"]["label"],
            "lat": feature["geometry"]["coordinates"][1],
            "lng": feature["geometry"]["coordinates"][0],
        }
        for feature in features
    ]
