from rest_framework import serializers
from .models import EVVehicle, ChargingStation, TripHistory


class OptimizeRouteSerializer(serializers.Serializer):
    source_lat = serializers.FloatField()
    source_lon = serializers.FloatField()
    destination_lat = serializers.FloatField()
    destination_lon = serializers.FloatField()
    vehicle_id = serializers.IntegerField()
    battery_percentage = serializers.FloatField()


class EVVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EVVehicle
        fields = '__all__'


class ChargingStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChargingStation
        fields = '__all__'


class TripHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TripHistory
        fields = '__all__'
