import requests
from route_optimizer.models import RouteCache

OSRM_BASE_URL = "http://router.project-osrm.org/route/v1/driving"

# In-memory cache (fast layer)
_route_cache = {}


def get_route(source_coords: tuple, destination_coords: tuple):
    """
    Fetch route from OSRM API with:
    - In-memory cache
    - DB persistent cache
    - Full geometry support
    """

    source_lon, source_lat = source_coords
    dest_lon, dest_lat = destination_coords

    cache_key = (source_lon, source_lat, dest_lon, dest_lat)

    # In-memory cache
    if cache_key in _route_cache:
        return _route_cache[cache_key]

    # DB persistent cache
    cached = RouteCache.objects.filter(
        source_lon=source_lon,
        source_lat=source_lat,
        dest_lon=dest_lon,
        dest_lat=dest_lat
    ).first()

    if cached:
        result = {
            "distance_km": cached.distance_km,
            "duration_min": cached.duration_min,
            "geometry": cached.geometry,
        }
        _route_cache[cache_key] = result
        return result

    # Call OSRM API
    source = f"{source_lon},{source_lat}"
    destination = f"{dest_lon},{dest_lat}"

    url = f"{OSRM_BASE_URL}/{source};{destination}?overview=full&geometries=geojson"

    response = requests.get(url)

    if response.status_code != 200:
        raise Exception("Failed to fetch route from OSRM")

    data = response.json()

    if not data.get("routes"):
        raise Exception("No route found")

    route = data["routes"][0]

    result = {
        "distance_km": route["distance"] / 1000,
        "duration_min": route["duration"] / 60,
        "geometry": route["geometry"],
    }

    # Save to DB persistent cache
    RouteCache.objects.get_or_create(
        source_lon=source_lon,
        source_lat=source_lat,
        dest_lon=dest_lon,
        dest_lat=dest_lat,
        defaults={
            "distance_km": result["distance_km"],
            "duration_min": result["duration_min"],
            "geometry": result["geometry"],
        }
    )

    # Save to memory cache
    _route_cache[cache_key] = result

    return result
