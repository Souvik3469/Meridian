from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .planner import plan_trip
from .serializers import TripRequestSerializer
from .services.exceptions import GeocodingError, RoutingError
from .services.geocoding import autocomplete

MIN_AUTOCOMPLETE_QUERY_LENGTH = 3


@api_view(['GET'])
def health_check(request):
    return Response({'status': 'ok'})


@api_view(['GET'])
def location_autocomplete(request):
    query_text = request.query_params.get('q', '').strip()
    if len(query_text) < MIN_AUTOCOMPLETE_QUERY_LENGTH:
        return Response({'results': []})

    try:
        results = autocomplete(query_text)
    except GeocodingError:
        # Suggestions are a soft-fail affordance, not the core flow — don't
        # surface an error banner just because the suggestion lookup failed.
        results = []

    return Response({'results': results})


class PlanTripView(APIView):
    def post(self, request):
        serializer = TripRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = plan_trip(**serializer.validated_data)
        except GeocodingError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except RoutingError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        return Response(result)
