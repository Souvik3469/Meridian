from django.test import SimpleTestCase

from trips.services.geometry import haversine_miles, point_at_distance


class HaversineMilesTests(SimpleTestCase):
    def test_one_degree_latitude_is_about_69_miles(self):
        distance = haversine_miles((0.0, 0.0), (1.0, 0.0))
        self.assertAlmostEqual(distance, 69.0, delta=1.0)

    def test_same_point_is_zero_distance(self):
        self.assertAlmostEqual(haversine_miles((10.0, 20.0), (10.0, 20.0)), 0.0)


class PointAtDistanceTests(SimpleTestCase):
    def setUp(self):
        # Three points spaced roughly 69 miles apart along a meridian.
        self.geometry = [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)]

    def test_zero_distance_returns_start(self):
        self.assertEqual(point_at_distance(self.geometry, 0), self.geometry[0])

    def test_midpoint_of_first_segment(self):
        lat, lng = point_at_distance(self.geometry, 34.5)
        self.assertAlmostEqual(lat, 0.5, delta=0.05)
        self.assertAlmostEqual(lng, 0.0)

    def test_distance_beyond_route_returns_last_point(self):
        self.assertEqual(point_at_distance(self.geometry, 1000), self.geometry[-1])

    def test_single_point_geometry_returns_that_point(self):
        self.assertEqual(point_at_distance([(5.0, 5.0)], 10), (5.0, 5.0))
