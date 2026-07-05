from unittest.mock import Mock, patch

import requests
from django.test import SimpleTestCase

from trips.services.exceptions import RoutingError
from trips.services.routing import get_route

SAMPLE_DIRECTIONS_RESPONSE = {
    "features": [
        {
            "properties": {
                "summary": {"distance": 160934.4, "duration": 7200.0},
                "segments": [
                    {"distance": 80467.2, "duration": 3600.0},
                    {"distance": 80467.2, "duration": 3600.0},
                ],
            },
            "geometry": {
                "coordinates": [
                    [-105.0178157, 39.7391536],
                    [-104.8, 39.5],
                    [-104.6, 39.2],
                ]
            },
        }
    ]
}


class GetRouteTests(SimpleTestCase):
    @patch("trips.services.routing.requests.post")
    def test_parses_distance_duration_and_legs(self, mock_post):
        mock_post.return_value = Mock(status_code=200, json=lambda: SAMPLE_DIRECTIONS_RESPONSE)

        result = get_route([(39.7391536, -105.0178157), (39.5, -104.8), (39.2, -104.6)])

        self.assertAlmostEqual(result.distance_miles, 100.0, places=3)
        self.assertAlmostEqual(result.duration_hours, 2.0, places=3)
        self.assertEqual(len(result.legs), 2)
        self.assertAlmostEqual(result.legs[0].distance_miles, 50.0, places=3)
        self.assertAlmostEqual(result.legs[0].duration_hours, 1.0, places=3)
        self.assertEqual(result.geometry[0], (39.7391536, -105.0178157))

    @patch("trips.services.routing.requests.post")
    def test_raises_on_non_200_response(self, mock_post):
        mock_post.return_value = Mock(status_code=404, text="not found")

        with self.assertRaises(RoutingError):
            get_route([(0, 0), (1, 1)])

    @patch("trips.services.routing.requests.post")
    def test_wraps_connection_errors_as_routing_error(self, mock_post):
        mock_post.side_effect = requests.ConnectionError("connection refused")

        with self.assertRaises(RoutingError):
            get_route([(0, 0), (1, 1)])

    @patch("trips.services.routing.requests.post")
    def test_raises_on_unexpected_response_shape(self, mock_post):
        mock_post.return_value = Mock(status_code=200, json=lambda: {"features": []})

        with self.assertRaises(RoutingError):
            get_route([(0, 0), (1, 1)])
