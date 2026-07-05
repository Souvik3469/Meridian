from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .planner import plan_trip
from .serializers import TripRequestSerializer
from .services.exceptions import GeocodingError, RoutingError


@api_view(['GET'])
def health_check(request):
    return Response({'status': 'ok'})


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
