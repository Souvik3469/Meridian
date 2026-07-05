from dataclasses import dataclass

import requests
from django.conf import settings

from .exceptions import RoutingError

ORS_DIRECTIONS_URL = "https://api.openrouteservice.org/v2/directions/driving-hgv/geojson"
METERS_PER_MILE = 1609.344
SECONDS_PER_HOUR = 3600


@dataclass
class RouteLegResult:
    distance_miles: float
    duration_hours: float


@dataclass
class RouteResult:
    distance_miles: float
    duration_hours: float
    geometry: list[tuple[float, float]]
    legs: list[RouteLegResult]


def get_route(waypoints: list[tuple[float, float]]) -> RouteResult:
    """Computes a route through the given (lat, lng) waypoints, in order.

    Returns the overall distance/duration/geometry plus a per-leg breakdown
    (one entry per consecutive pair of waypoints), so the HOS engine can
    simulate each drive segment independently.
    """
    try:
        response = requests.post(
            ORS_DIRECTIONS_URL,
            json={"coordinates": [[lng, lat] for lat, lng in waypoints]},
            headers={
                "Authorization": settings.OPENROUTESERVICE_API_KEY,
                "Content-Type": "application/json",
            },
            timeout=15,
        )
    except requests.RequestException as exc:
        raise RoutingError(f"Routing request failed: {exc}") from exc

    if response.status_code != 200:
        raise RoutingError(f"Routing request failed: {response.status_code} {response.text}")

    try:
        feature = response.json()["features"][0]
        summary = feature["properties"]["summary"]
        segments = feature["properties"]["segments"]
        geometry = [(lat, lng) for lng, lat in feature["geometry"]["coordinates"]]
    except (KeyError, IndexError) as exc:
        raise RoutingError("Unexpected routing response format") from exc

    return RouteResult(
        distance_miles=summary["distance"] / METERS_PER_MILE,
        duration_hours=summary["duration"] / SECONDS_PER_HOUR,
        geometry=geometry,
        legs=[
            RouteLegResult(
                distance_miles=segment["distance"] / METERS_PER_MILE,
                duration_hours=segment["duration"] / SECONDS_PER_HOUR,
            )
            for segment in segments
        ],
    )
