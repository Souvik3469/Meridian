from .hos.engine import RouteLeg, build_duty_schedule, split_into_days
from .services.geocoding import geocode
from .services.geometry import point_at_distance
from .services.routing import get_route

# Duty-status labels that should also show up as pins on the map.
STOP_TYPES_BY_LABEL = {
    "30-minute break": "rest",
    "10-hour rest period": "rest",
    "34-hour restart": "rest",
    "Fuel stop": "fuel",
}


def plan_trip(
    current_location: str,
    pickup_location: str,
    dropoff_location: str,
    current_cycle_used_hours: float,
    trip_start_time=None,
) -> dict:
    current_coords = geocode(current_location)
    pickup_coords = geocode(pickup_location)
    dropoff_coords = geocode(dropoff_location)

    route = get_route([current_coords, pickup_coords, dropoff_coords])
    to_pickup_leg, to_dropoff_leg = route.legs

    trip_start_hour = trip_start_time.hour + trip_start_time.minute / 60 if trip_start_time else 0.0

    entries = build_duty_schedule(
        current_cycle_used_hours,
        RouteLeg(to_pickup_leg.distance_miles, to_pickup_leg.duration_hours, "En route to pickup"),
        RouteLeg(to_dropoff_leg.distance_miles, to_dropoff_leg.duration_hours, "En route to dropoff"),
        trip_start_hour,
    )

    stops = [
        {"type": "current", "label": current_location, "lat": current_coords[0], "lng": current_coords[1]},
        {"type": "pickup", "label": pickup_location, "lat": pickup_coords[0], "lng": pickup_coords[1]},
        {"type": "dropoff", "label": dropoff_location, "lat": dropoff_coords[0], "lng": dropoff_coords[1]},
    ]
    for entry in entries:
        stop_type = STOP_TYPES_BY_LABEL.get(entry.label)
        if stop_type is None:
            continue
        lat, lng = point_at_distance(route.geometry, entry.distance_marker_miles)
        stops.append({"type": stop_type, "label": entry.label, "lat": lat, "lng": lng})

    return {
        "route": {
            "distance_miles": route.distance_miles,
            "duration_hours": route.duration_hours,
            "geometry": [[lat, lng] for lat, lng in route.geometry],
            "stops": stops,
        },
        "days": [
            {
                "day_number": day.day_number,
                "entries": [
                    {
                        "status": entry.status.value,
                        "start_hour": entry.start_hour,
                        "end_hour": entry.end_hour,
                        "label": entry.label,
                    }
                    for entry in day.entries
                ],
                "totals": day.totals,
            }
            for day in split_into_days(entries)
        ],
        "summary": {
            "total_trip_hours": entries[-1].end_hour if entries else 0.0,
            "requires_34_hour_restart": any(entry.label == "34-hour restart" for entry in entries),
        },
    }
