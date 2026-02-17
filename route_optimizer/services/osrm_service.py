import requests


OSRM_BASE_URL = "http://router.project-osrm.org/route/v1/driving"


def get_route(source_coords: tuple, destination_coords: tuple):
    """
    Fetch route from OSRM API.
    
    :param source_coords: (longitude, latitude)
    :param destination_coords: (longitude, latitude)
    :return: dict with distance (km), duration (minutes), geometry (geojson)
    """

    source = f"{source_coords[0]},{source_coords[1]}"
    destination = f"{destination_coords[0]},{destination_coords[1]}"

    url = f"{OSRM_BASE_URL}/{source};{destination}?overview=full&geometries=geojson"

    response = requests.get(url)

    if response.status_code != 200:
        raise Exception("Failed to fetch route from OSRM")

    data = response.json()

    if "routes" not in data or not data["routes"]:
        raise Exception("No route found")

    route = data["routes"][0]

    return {
        "distance_km": route["distance"] / 1000,
        "duration_min": route["duration"] / 60,
        "geometry": route["geometry"],
    }
