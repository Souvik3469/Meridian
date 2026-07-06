from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIClient

from trips.services.exceptions import GeocodingError, RoutingError
from trips.services.routing import RouteLegResult, RouteResult

SAMPLE_ROUTE = RouteResult(
    distance_miles=520.0,
    duration_hours=9.0,
    geometry=[(39.7, -105.0), (36.0, -104.0), (35.1, -106.6)],
    legs=[
        RouteLegResult(distance_miles=70.0, duration_hours=1.2),
        RouteLegResult(distance_miles=450.0, duration_hours=7.8),
    ],
)


class PlanTripViewTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_payload = {
            "current_location": "Denver, CO",
            "pickup_location": "Colorado Springs, CO",
            "dropoff_location": "Albuquerque, NM",
            "current_cycle_used_hours": 10,
        }

    @patch("trips.planner.get_route", return_value=SAMPLE_ROUTE)
    @patch("trips.planner.geocode", return_value=(39.7, -105.0))
    def test_returns_route_and_days_for_valid_request(self, mock_geocode, mock_get_route):
        response = self.client.post("/api/trips/plan/", self.valid_payload, format="json")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("route", body)
        self.assertIn("days", body)
        self.assertGreater(len(body["days"]), 0)
        self.assertEqual(body["route"]["distance_miles"], 520.0)
        stop_types = {stop["type"] for stop in body["route"]["stops"]}
        self.assertIn("pickup", stop_types)
        self.assertIn("dropoff", stop_types)
        self.assertIn("summary", body)
        self.assertFalse(body["summary"]["requires_34_hour_restart"])
        self.assertGreater(body["summary"]["total_trip_hours"], 0)

    @patch("trips.planner.get_route", return_value=SAMPLE_ROUTE)
    @patch("trips.planner.geocode", return_value=(39.7, -105.0))
    def test_summary_flags_when_cycle_hours_force_a_restart(self, mock_geocode, mock_get_route):
        payload = {**self.valid_payload, "current_cycle_used_hours": 69}
        response = self.client.post("/api/trips/plan/", payload, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["summary"]["requires_34_hour_restart"])

    def test_rejects_missing_fields(self):
        response = self.client.post("/api/trips/plan/", {}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_rejects_cycle_hours_over_seventy(self):
        payload = {**self.valid_payload, "current_cycle_used_hours": 71}
        response = self.client.post("/api/trips/plan/", payload, format="json")
        self.assertEqual(response.status_code, 400)

    @patch("trips.planner.geocode", side_effect=GeocodingError("No location found for 'Nowhereville'"))
    def test_geocoding_failure_returns_400(self, mock_geocode):
        response = self.client.post("/api/trips/plan/", self.valid_payload, format="json")
        self.assertEqual(response.status_code, 400)

    @patch("trips.planner.get_route", side_effect=RoutingError("Routing request failed"))
    @patch("trips.planner.geocode", return_value=(39.7, -105.0))
    def test_routing_failure_returns_502(self, mock_geocode, mock_get_route):
        response = self.client.post("/api/trips/plan/", self.valid_payload, format="json")
        self.assertEqual(response.status_code, 502)
