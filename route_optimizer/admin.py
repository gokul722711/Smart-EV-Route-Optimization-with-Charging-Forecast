from django.contrib import admin
from .models import EVVehicle, ChargingStation, TripHistory


admin.site.register(EVVehicle)
admin.site.register(ChargingStation)
admin.site.register(TripHistory)
