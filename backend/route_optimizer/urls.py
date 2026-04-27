from django.urls import path
from .views import (
    OptimizeRouteView,
    VehicleListView,
    ChargingStationListView,
    TripHistoryListView,
    TripHistoryClearView,
    HealthCheckView,
)

urlpatterns = [
    path("optimize-route/", OptimizeRouteView.as_view(), name="optimize-route"),
    path("vehicles/", VehicleListView.as_view(), name="vehicle-list"),
    path("stations/", ChargingStationListView.as_view(), name="station-list"),
    path("trips/", TripHistoryListView.as_view(), name="trip-history"),
    path("trips/clear/", TripHistoryClearView.as_view(), name="trip-history-clear"),
    path("health/", HealthCheckView.as_view(), name="health-check"),
]
