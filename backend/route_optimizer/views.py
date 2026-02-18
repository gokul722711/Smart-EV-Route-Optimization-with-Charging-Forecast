from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import OptimizeRouteSerializer
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

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
