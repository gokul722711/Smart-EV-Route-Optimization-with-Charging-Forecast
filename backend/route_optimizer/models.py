from django.db import models


class EVVehicle(models.Model):
    name = models.CharField(max_length=100)
    battery_capacity_kwh = models.FloatField()
    max_range_km = models.FloatField()
    efficiency_km_per_kwh = models.FloatField()

    def __str__(self):
        return self.name


class ChargingStation(models.Model):
    name = models.CharField(max_length=150)
    latitude = models.FloatField()
    longitude = models.FloatField()
    total_slots = models.IntegerField()
    fast_charger = models.BooleanField(default=False)
    power_kw = models.FloatField()

    def __str__(self):
        return self.name


class TripHistory(models.Model):
    source = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    distance_km = models.FloatField()
    battery_used_percentage = models.FloatField()
    charging_stops = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source} → {self.destination}"

class RouteCache(models.Model):
    source_lon = models.FloatField()
    source_lat = models.FloatField()
    dest_lon = models.FloatField()
    dest_lat = models.FloatField()

    distance_km = models.FloatField()
    duration_min = models.FloatField()
    geometry = models.JSONField(default=dict)

    class Meta:
        unique_together = (
            "source_lon",
            "source_lat",
            "dest_lon",
            "dest_lat",
        )


