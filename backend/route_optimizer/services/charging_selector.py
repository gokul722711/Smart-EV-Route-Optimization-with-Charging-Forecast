import math
from typing import List
from route_optimizer.models import ChargingStation


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two lat/lon points in kilometers.
    """
    R = 6371  # Earth radius in km

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1)
        * math.cos(phi2)
        * math.sin(d_lambda / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def is_station_near_route(
    station_lat,
    station_lon,
    route_coordinates,
    threshold_km=10
):
    """
    Check if charging station is within threshold_km
    of any route coordinate point.
    """

    for coord in route_coordinates:
        lon, lat = coord
        distance = haversine_distance(
            lat, lon,
            station_lat, station_lon
        )
        if distance <= threshold_km:
            return True

    return False


def get_nearby_stations(route_geometry: dict) -> List[ChargingStation]:
    """
    Return charging stations near the route.
    """

    route_coordinates = route_geometry["coordinates"]

    stations = ChargingStation.objects.all()

    nearby = []

    for station in stations:
        if is_station_near_route(
            station.latitude,
            station.longitude,
            route_coordinates
        ):
            nearby.append(station)

    # Sort:
    # Fast chargers first, then by power
    nearby.sort(
        key=lambda s: (
            not s.fast_charger,
            -s.power_kw
        )
    )

    return nearby
