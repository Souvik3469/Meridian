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

SAMPLE_ROUTE_THREE_STOPS = RouteResult(
    distance_miles=720.0,
    duration_hours=12.0,
    geometry=[(39.7, -105.0), (36.0, -104.0), (35.1, -106.6), (33.4, -108.1)],
    legs=[
        RouteLegResult(distance_miles=70.0, duration_hours=1.2),
        RouteLegResult(distance_miles=450.0, duration_hours=7.8),
        RouteLegResult(distance_miles=200.0, duration_hours=3.0),
    ],
)


class PlanTripViewTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_payload = {
            "current_location": "Denver, CO",
            "stops": [
                {"location": "Colorado Springs, CO", "type": "pickup"},
                {"location": "Albuquerque, NM", "type": "dropoff"},
            ],
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

    @patch("trips.planner.get_route", return_value=SAMPLE_ROUTE)
    @patch("trips.planner.geocode", return_value=(39.7, -105.0))
    def test_accepts_optional_trip_start_time(self, mock_geocode, mock_get_route):
        payload = {**self.valid_payload, "trip_start_time": "06:30"}
        response = self.client.post("/api/trips/plan/", payload, format="json")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        first_entry = body["days"][0]["entries"][0]
        self.assertEqual(first_entry["status"], "off_duty")
        self.assertAlmostEqual(first_entry["end_hour"], 6.5)

    @patch("trips.planner.get_route", return_value=SAMPLE_ROUTE_THREE_STOPS)
    @patch("trips.planner.geocode", return_value=(39.7, -105.0))
    def test_accepts_more_than_two_stops(self, mock_geocode, mock_get_route):
        payload = {
            **self.valid_payload,
            "stops": [
                {"location": "Colorado Springs, CO", "type": "pickup"},
                {"location": "Albuquerque, NM", "type": "dropoff"},
                {"location": "Santa Fe, NM", "type": "pickup"},
            ],
        }
        response = self.client.post("/api/trips/plan/", payload, format="json")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        stop_labels = {stop["label"] for stop in body["route"]["stops"]}
        self.assertIn("Colorado Springs, CO", stop_labels)
        self.assertIn("Albuquerque, NM", stop_labels)
        self.assertIn("Santa Fe, NM", stop_labels)

    @patch("trips.planner.get_route", return_value=SAMPLE_ROUTE)
    @patch("trips.planner.geocode", return_value=(39.7, -105.0))
    def test_extra_delay_hours_extends_the_trip(self, mock_geocode, mock_get_route):
        baseline = self.client.post("/api/trips/plan/", self.valid_payload, format="json").json()

        delayed_payload = {
            **self.valid_payload,
            "stops": [
                {"location": "Colorado Springs, CO", "type": "pickup", "extra_delay_hours": 2},
                {"location": "Albuquerque, NM", "type": "dropoff"},
            ],
        }
        response = self.client.post("/api/trips/plan/", delayed_payload, format="json")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertAlmostEqual(
            body["summary"]["total_trip_hours"],
            baseline["summary"]["total_trip_hours"] + 2,
            places=3,
        )

    def test_rejects_fewer_than_two_stops(self):
        payload = {**self.valid_payload, "stops": [{"location": "Colorado Springs, CO", "type": "pickup"}]}
        response = self.client.post("/api/trips/plan/", payload, format="json")
        self.assertEqual(response.status_code, 400)

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


class LocationAutocompleteViewTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    @patch("trips.views.autocomplete", return_value=[{"label": "Denver, CO, USA", "lat": 39.7, "lng": -105.0}])
    def test_returns_suggestions_for_valid_query(self, mock_autocomplete):
        response = self.client.get("/api/locations/autocomplete/", {"q": "Denv"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 1)
        mock_autocomplete.assert_called_once_with("Denv")

    def test_short_query_skips_the_lookup_entirely(self):
        with patch("trips.views.autocomplete") as mock_autocomplete:
            response = self.client.get("/api/locations/autocomplete/", {"q": "De"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"], [])
        mock_autocomplete.assert_not_called()

    @patch("trips.views.autocomplete", side_effect=GeocodingError("boom"))
    def test_geocoding_error_soft_fails_to_empty_results(self, mock_autocomplete):
        response = self.client.get("/api/locations/autocomplete/", {"q": "Denver"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"], [])
