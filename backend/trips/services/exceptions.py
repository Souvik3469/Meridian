class GeocodingError(Exception):
    """Raised when a location string can't be resolved to coordinates."""


class RoutingError(Exception):
    """Raised when a route can't be computed between the given coordinates."""
