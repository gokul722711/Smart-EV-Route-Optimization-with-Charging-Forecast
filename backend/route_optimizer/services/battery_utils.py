def calculate_remaining_range(
    battery_percentage: float,
    max_range_km: float
) -> float:
    """
    Calculate how many kilometers the vehicle can travel
    based on current battery percentage.
    """
    return (battery_percentage / 100) * max_range_km


def is_charging_required(
    route_distance_km: float,
    remaining_range_km: float
) -> bool:
    """
    Check whether charging is required for the trip.
    """
    return route_distance_km > remaining_range_km


def estimate_charging_time(
    required_km: float,
    efficiency_km_per_kwh: float,
    charger_power_kw: float
) -> float:
    """
    Estimate charging time in minutes.
    
    Steps:
    1. Convert required distance to energy needed.
    2. Charging time = energy / charger power.
    """
    required_energy_kwh = required_km / efficiency_km_per_kwh
    charging_hours = required_energy_kwh / charger_power_kw
    return charging_hours * 60  # convert to minutes
