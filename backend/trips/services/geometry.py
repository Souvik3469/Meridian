import math

EARTH_RADIUS_MILES = 3958.8


def haversine_miles(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    lat1, lng1 = p1
    lat2, lng2 = p2
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * EARTH_RADIUS_MILES * math.asin(math.sqrt(a))


def point_at_distance(
    geometry: list[tuple[float, float]], target_distance_miles: float
) -> tuple[float, float]:
    """Walks `geometry` (a polyline of (lat, lng) points) and returns the
    point `target_distance_miles` along it from the start, linearly
    interpolating within whichever segment contains that distance."""
    if not geometry:
        raise ValueError("geometry must not be empty")
    if target_distance_miles <= 0 or len(geometry) == 1:
        return geometry[0]

    cumulative = 0.0
    for p1, p2 in zip(geometry, geometry[1:]):
        segment_miles = haversine_miles(p1, p2)
        if cumulative + segment_miles >= target_distance_miles:
            remaining = target_distance_miles - cumulative
            fraction = remaining / segment_miles if segment_miles > 0 else 0.0
            lat = p1[0] + (p2[0] - p1[0]) * fraction
            lng = p1[1] + (p2[1] - p1[1]) * fraction
            return (lat, lng)
        cumulative += segment_miles

    return geometry[-1]
