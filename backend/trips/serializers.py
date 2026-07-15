from rest_framework import serializers


class TripStopSerializer(serializers.Serializer):
    location = serializers.CharField(max_length=255)
    type = serializers.ChoiceField(choices=["pickup", "dropoff"])


class TripRequestSerializer(serializers.Serializer):
    current_location = serializers.CharField(max_length=255)
    stops = TripStopSerializer(many=True)
    current_cycle_used_hours = serializers.FloatField(min_value=0, max_value=70)
    trip_start_time = serializers.TimeField(required=False, allow_null=True, default=None)

    def validate_stops(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("At least a pickup and a dropoff stop are required.")
        return value
