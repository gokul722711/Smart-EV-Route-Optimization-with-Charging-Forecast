import requests

OSRM_BASE_URL = "http://router.project-osrm.org/route/v1/driving"

# In-memory cache
_route_cache = {}


def get_route(source_coords: tuple, destination_coords: tuple):
    """
    Fetch route from OSRM API with caching.
    """

    cache_key = (source_coords, destination_coords)

    if cache_key in _route_cache:
        return _route_cache[cache_key]

    source = f"{source_coords[0]},{source_coords[1]}"
    destination = f"{destination_coords[0]},{destination_coords[1]}"

    url = f"{OSRM_BASE_URL}/{source};{destination}?overview=false"

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
    }

    _route_cache[cache_key] = result

    return result
