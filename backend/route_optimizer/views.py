from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView

from .models import EVVehicle, ChargingStation, TripHistory
from .serializers import (
    OptimizeRouteSerializer,
    EVVehicleSerializer,
    ChargingStationSerializer,
    TripHistorySerializer,
)
from route_optimizer.services.route_optimizer_service import optimize_route


class OptimizeRouteView(APIView):

    def post(self, request):
        serializer = OptimizeRouteSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        try:
            result = optimize_route(
                source_coords=(data["source_lon"], data["source_lat"]),
                destination_coords=(data["destination_lon"], data["destination_lat"]),
                vehicle_id=data["vehicle_id"],
                battery_percentage=data["battery_percentage"],
            )

            # If route was found successfully, save to trip history
            if "error" not in result:
                total_distance = sum(
                    seg.get("distance_km", 0)
                    for seg in result.get("route_segments", [])
                )
                TripHistory.objects.create(
                    source=f"{data['source_lat']}, {data['source_lon']}",
                    destination=f"{data['destination_lat']}, {data['destination_lon']}",
                    distance_km=round(total_distance, 2),
                    battery_used_percentage=data["battery_percentage"],
                    charging_stops=result.get("charging_stops", []),
                )

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VehicleListView(ListAPIView):
    """List all available EV vehicles."""
    queryset = EVVehicle.objects.all()
    serializer_class = EVVehicleSerializer


class ChargingStationListView(ListAPIView):
    """List all charging stations."""
    queryset = ChargingStation.objects.all()
    serializer_class = ChargingStationSerializer


class TripHistoryListView(ListAPIView):
    """List trip history, most recent first."""
    queryset = TripHistory.objects.all().order_by('-created_at')
    serializer_class = TripHistorySerializer


class TripHistoryClearView(APIView):
    """Clear all trip history entries."""

    def delete(self, request):
        deleted_count, _ = TripHistory.objects.all().delete()
        return Response({"deleted": deleted_count}, status=status.HTTP_200_OK)


class HealthCheckView(APIView):
    """Simple health check endpoint for frontend connectivity status."""

    def get(self, request):
        return Response({"status": "ok"}, status=status.HTTP_200_OK)
