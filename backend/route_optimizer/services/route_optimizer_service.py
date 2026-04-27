import math

from route_optimizer.models import EVVehicle, ChargingStation
from route_optimizer.services.osrm_service import get_route
from route_optimizer.services.battery_utils import calculate_remaining_range
from route_optimizer.services.pathfinding import astar_state_search

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2)
        * math.sin(d_lambda / 2) ** 2
    )

    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def optimize_route(
    source_coords: tuple,
    destination_coords: tuple,
    vehicle_id: int,
    battery_percentage: float,
):
    vehicle = EVVehicle.objects.get(id=vehicle_id)

    max_range = vehicle.max_range_km
    initial_battery = calculate_remaining_range(
        battery_percentage,
        max_range
    )

    nodes = {
        "source": source_coords,
        "destination": destination_coords,
    }

    stations = ChargingStation.objects.all()

    for station in stations:
        nodes[station.name] = (station.longitude, station.latitude)

    def get_distance(a, b):
        route = get_route(a, b)
        return route["distance_km"], route["duration_min"]

    def get_charger_power(node_name):
        station = ChargingStation.objects.filter(name=node_name).first()
        return station.power_kw if station else 1

    dest_lon, dest_lat = destination_coords

    def heuristic(node):
        lon, lat = nodes[node]
        return haversine_distance(lat, lon, dest_lat, dest_lon)

    result = astar_state_search(
        nodes=nodes,
        get_distance_func=get_distance,
        start_node="source",
        end_node="destination",
        max_range=max_range,
        initial_battery=initial_battery,
        vehicle_efficiency=vehicle.efficiency_km_per_kwh,
        get_charger_power=get_charger_power,
        heuristic=heuristic
    )

    # No feasible path
    if not result:
        return {"error": "No feasible route found"}

    state_path = result["path"]
    total_cost = result["total_cost"]

    route_segments = []
    charging_stops = []

    for i in range(len(state_path) - 1):
        from_node, from_battery = state_path[i]
        to_node, to_battery = state_path[i + 1]

        # Charging event (same node, battery increased)
        if from_node == to_node and to_battery > from_battery:
            charging_stops.append({
                "node": from_node,
                "battery_after_charge": round(to_battery, 2)
            })
            continue

        # Travel segment
        from_coords = nodes[from_node]
        to_coords = nodes[to_node]

        full_route = get_route(from_coords, to_coords)

        route_segments.append({
            "from": from_node,
            "to": to_node,
            "distance_km": round(full_route["distance_km"], 2),
            "duration_min": round(full_route["duration_min"], 2),
            "geometry": full_route.get("geometry")
        })


    return {
        "total_time_min": round(total_cost, 2),
        "initial_battery_km": round(initial_battery, 2),
        "path": state_path,
        "charging_stops": charging_stops,
        "route_segments": route_segments
    }
