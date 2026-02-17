from route_optimizer.models import EVVehicle
from route_optimizer.services.osrm_service import get_route
from route_optimizer.services.battery_utils import (
    calculate_remaining_range,
    is_charging_required,
    estimate_charging_time,
)
from route_optimizer.services.charging_selector import get_nearby_stations


def optimize_route(
    source_coords: tuple,
    destination_coords: tuple,
    vehicle_id: int,
    battery_percentage: float,
):
    """
    Main EV route optimization engine.
    """

    # 1️⃣ Fetch route
    route_data = get_route(source_coords, destination_coords)

    distance_km = route_data["distance_km"]
    duration_min = route_data["duration_min"]
    geometry = route_data["geometry"]

    # 2️⃣ Get vehicle
    vehicle = EVVehicle.objects.get(id=vehicle_id)

    # 3️⃣ Calculate remaining range
    remaining_range = calculate_remaining_range(
        battery_percentage,
        vehicle.max_range_km,
    )

    # 4️⃣ Check charging necessity
    charging_required = is_charging_required(
        distance_km,
        remaining_range,
    )

    charging_stops_data = []

    if charging_required:
        # 5️⃣ Get nearby stations
        stations = get_nearby_stations(geometry)

        if stations:
            selected_station = stations[0]  # Best station (sorted earlier)

            required_km = distance_km - remaining_range

            charge_time = estimate_charging_time(
                required_km,
                vehicle.efficiency_km_per_kwh,
                selected_station.power_kw,
            )

            charging_stops_data.append({
                "name": selected_station.name,
                "latitude": selected_station.latitude,
                "longitude": selected_station.longitude,
                "estimated_charge_time_min": round(charge_time, 2),
            })

    return {
        "distance_km": round(distance_km, 2),
        "duration_min": round(duration_min, 2),
        "remaining_range_km": round(remaining_range, 2),
        "charging_required": charging_required,
        "charging_stops": charging_stops_data,
        "geometry": geometry,
    }
