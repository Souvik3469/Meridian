from unittest.mock import Mock, patch

import requests
from django.test import SimpleTestCase

from trips.services.exceptions import GeocodingError
from trips.services.geocoding import geocode


class GeocodeTests(SimpleTestCase):
    @patch("trips.services.geocoding.requests.get")
    def test_returns_lat_lng_for_first_feature(self, mock_get):
        mock_get.return_value = Mock(
            json=lambda: {
                "features": [
                    {"geometry": {"coordinates": [-105.0178157, 39.7391536], "type": "Point"}},
                ]
            }
        )

        lat, lng = geocode("Denver, CO")

        self.assertAlmostEqual(lat, 39.7391536)
        self.assertAlmostEqual(lng, -105.0178157)

    @patch("trips.services.geocoding.requests.get")
    def test_raises_when_no_features_found(self, mock_get):
        mock_get.return_value = Mock(json=lambda: {"features": []})

        with self.assertRaises(GeocodingError):
            geocode("Nowhere in particular")

    @patch("trips.services.geocoding.requests.get")
    def test_wraps_http_errors_as_geocoding_error(self, mock_get):
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError("401 Client Error: Unauthorized")
        mock_get.return_value = response

        with self.assertRaises(GeocodingError):
            geocode("Denver, CO")
