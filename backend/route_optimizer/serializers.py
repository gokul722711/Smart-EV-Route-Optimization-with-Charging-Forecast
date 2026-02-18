from rest_framework import serializers


class OptimizeRouteSerializer(serializers.Serializer):
    source_lat = serializers.FloatField()
    source_lon = serializers.FloatField()
    destination_lat = serializers.FloatField()
    destination_lon = serializers.FloatField()
    vehicle_id = serializers.IntegerField()
    battery_percentage = serializers.FloatField()
