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


def _point_to_segment_distance(px, py, ax, ay, bx, by):
    """
    Approximate perpendicular distance from point P(px,py)
    to the line segment A(ax,ay)-B(bx,by), using lat/lon as flat coords.
    Returns haversine distance to the closest point on the segment.
    """
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return haversine_distance(px, py, ax, ay)

    t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    proj_lat = ax + t * dx
    proj_lon = ay + t * dy
    return haversine_distance(px, py, proj_lat, proj_lon)


def _filter_nearby_stations(source_coords, destination_coords, max_range, max_stations=15):
    """
    Pre-filter charging stations to only those within the route corridor.
    This prevents the A* search from exploring 120+ nodes.

    Strategy:
    1. Keep stations within (buffer_km) of the source→destination line segment.
    2. Buffer = max(max_range * 0.6, 50km) to ensure reachable stations are included.
    3. Cap at max_stations, sorted by distance to the corridor midpoint.
    """
    src_lon, src_lat = source_coords
    dst_lon, dst_lat = destination_coords

    direct_distance = haversine_distance(src_lat, src_lon, dst_lat, dst_lon)

    # Buffer: at least 50km, up to 60% of vehicle range, but not more than
    # half the trip distance (for short trips, keep a tight corridor)
    buffer_km = min(
        max(max_range * 0.6, 50),
        max(direct_distance * 0.5, 50)
    )

    stations = ChargingStation.objects.all()
    candidates = []

    for station in stations:
        # Distance from station to the source→destination line segment
        corridor_dist = _point_to_segment_distance(
            station.latitude, station.longitude,
            src_lat, src_lon,
            dst_lat, dst_lon,
        )

        if corridor_dist <= buffer_km:
            # Also compute distance from source (for sorting relevance)
            dist_from_src = haversine_distance(
                station.latitude, station.longitude, src_lat, src_lon
            )
            candidates.append((station, corridor_dist, dist_from_src))

    # Sort by corridor distance (closest to the route first), then cap
    candidates.sort(key=lambda x: x[1])

    return [c[0] for c in candidates[:max_stations]]


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

    # Pre-filter: only stations near the route corridor (max 15)
    nearby_stations = _filter_nearby_stations(
        source_coords, destination_coords, max_range
    )

    # Build a power lookup dict to avoid repeated DB queries during search
    charger_power_map = {}
    for station in nearby_stations:
        nodes[station.name] = (station.longitude, station.latitude)
        charger_power_map[station.name] = station.power_kw

    def get_distance(a, b):
        route = get_route(a, b)
        return route["distance_km"], route["duration_min"]

    def get_charger_power(node_name):
        return charger_power_map.get(node_name, 1)

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