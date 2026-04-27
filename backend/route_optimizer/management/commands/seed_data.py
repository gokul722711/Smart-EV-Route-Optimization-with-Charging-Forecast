"""
Django management command to seed the database with realistic Indian EV data.

Usage:
    python manage.py seed_data          # Seed all data
    python manage.py seed_data --flush  # Clear existing data first, then seed
"""

from django.core.management.base import BaseCommand
from route_optimizer.models import EVVehicle, ChargingStation


# ─────────────────────────────────────────────────────────────────────────────
# EV VEHICLE DATA — 25 real/realistic Indian-market EV models
# ─────────────────────────────────────────────────────────────────────────────
EV_VEHICLES = [
    # name, battery_capacity_kwh, max_range_km, efficiency_km_per_kwh
    ("Tata Nexon EV Max LR", 40.5, 437, 10.79),
    ("Tata Nexon EV Prime", 30.2, 312, 10.33),
    ("Tata Punch EV Adventure LR", 35.0, 421, 12.03),
    ("Tata Punch EV Smart", 25.0, 315, 12.60),
    ("Tata Tiago EV", 24.0, 315, 13.13),
    ("Tata Curvv EV", 55.0, 585, 10.64),
    ("MG ZS EV Excite", 50.3, 461, 9.17),
    ("MG Comet EV", 17.3, 230, 13.29),
    ("MG Windsor EV", 38.0, 331, 8.71),
    ("Hyundai Creta EV Long Range", 51.4, 473, 9.20),
    ("Hyundai Creta EV", 42.0, 390, 9.29),
    ("Hyundai Ioniq 5", 72.6, 631, 8.69),
    ("Mahindra XEV 9e Pack Three", 59.2, 542, 9.15),
    ("Mahindra BE 6e Pack Three", 59.2, 535, 9.04),
    ("Mahindra XUV400 EL Pro", 39.4, 456, 11.57),
    ("Kia EV6 GT-Line AWD", 77.4, 708, 9.15),
    ("Kia EV9", 99.8, 561, 5.62),
    ("BYD Atto 3", 60.5, 521, 8.61),
    ("BYD Seal", 82.5, 650, 7.88),
    ("BYD e6", 71.7, 520, 7.25),
    ("Citroen eC3", 29.2, 320, 10.96),
    ("BMW iX1 xDrive30", 66.5, 440, 6.62),
    ("Mercedes EQS 580", 107.8, 857, 7.95),
    ("Volvo XC40 Recharge", 78.0, 592, 7.59),
    ("Audi Q8 e-tron", 114.0, 600, 5.26),
]


# ─────────────────────────────────────────────────────────────────────────────
# CHARGING STATION DATA — Reduced set of stations per user request
# Format: (name, latitude, longitude, total_slots, fast_charger, power_kw)
# ─────────────────────────────────────────────────────────────────────────────
CHARGING_STATIONS = [
    # ── METRO & MAJOR CITIES ──────────────────────────────────────────
    ("ChargeZone Supercharger - Delhi", 28.6139, 77.2090, 8, True, 120),
    ("Tata Power - BKC Mumbai", 19.0658, 72.8686, 6, True, 60),
    ("Ather Grid HQ - Bengaluru", 12.9716, 77.5946, 6, True, 60),
    ("TNEB EV Hub - Chennai", 13.0827, 80.2707, 6, True, 120),
    ("ChargeZone Supercharger - Hyderabad", 17.3850, 78.4867, 8, True, 150),
    ("CESC EV Hub - Kolkata", 22.5726, 88.3639, 6, True, 120),
    ("Statiq Supercharger - Ahmedabad", 23.0225, 72.5714, 8, True, 150),
    ("Tata Power - Jaipur", 26.9124, 75.7873, 4, True, 60),
    ("Statiq Charge - Lucknow", 26.8467, 80.9462, 4, True, 60),
    ("ChargeZone - Chandigarh", 30.7333, 76.7794, 4, True, 50),
    
    # ── TIER 2/3 & TRANSIT HUBS ───────────────────────────────────────
    ("Tata Power - Pune", 18.5204, 73.8567, 4, True, 50),
    ("ChargeZone - Hosur", 12.7332, 77.8286, 4, True, 60),
    ("IOCL Charge - Nagpur", 21.1458, 79.0882, 4, True, 60),
    ("KSEB EV Hub - Kochi", 9.9312, 76.2673, 6, True, 60),
    ("Tata Power - Bhopal", 23.2599, 77.4126, 4, True, 60),
    ("Tata Power - Guwahati", 26.1445, 91.7362, 4, True, 60),
    ("IOCL Charge - Amritsar", 31.6340, 74.8723, 2, False, 22),
    ("Kazam EV - Udaipur", 24.5854, 73.7125, 2, False, 22),
    ("Tata Power - Panaji Goa", 15.4989, 73.8278, 4, True, 60),
    ("IOCL Charge - Bhubaneswar", 20.2961, 85.8245, 4, True, 50),
    ("BPCL Charge - Prayagraj", 25.4358, 81.8463, 2, False, 15),
    ("Statiq Charge - Gwalior", 26.2183, 78.1828, 3, True, 50),
    ("ChargeZone - Hubli", 15.3647, 75.1240, 2, False, 22),
    ("IOCL Charge - Salem", 11.6643, 78.1460, 2, False, 22),
]


class Command(BaseCommand):
    help = "Seed the database with 25 EV vehicle models and 120 charging stations across India"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Clear existing EVVehicle and ChargingStation data before seeding",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write(self.style.WARNING("Flushing existing data..."))
            EVVehicle.objects.all().delete()
            ChargingStation.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("  ✓ Cleared all vehicles and stations"))

        # ── Seed Vehicles ────────────────────────────────────────────────
        self.stdout.write(self.style.HTTP_INFO("\n🚗 Seeding EV Vehicles..."))
        vehicles_created = 0
        vehicles_skipped = 0

        for name, battery, max_range, efficiency in EV_VEHICLES:
            _, created = EVVehicle.objects.get_or_create(
                name=name,
                defaults={
                    "battery_capacity_kwh": battery,
                    "max_range_km": max_range,
                    "efficiency_km_per_kwh": efficiency,
                },
            )
            if created:
                vehicles_created += 1
                self.stdout.write(f"  + {name}")
            else:
                vehicles_skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"  ✓ Vehicles: {vehicles_created} created, {vehicles_skipped} already existed"
            )
        )

        # ── Seed Charging Stations ───────────────────────────────────────
        self.stdout.write(self.style.HTTP_INFO("\n⚡ Seeding Charging Stations..."))
        stations_created = 0
        stations_skipped = 0

        for name, lat, lon, slots, fast, power in CHARGING_STATIONS:
            _, created = ChargingStation.objects.get_or_create(
                name=name,
                defaults={
                    "latitude": lat,
                    "longitude": lon,
                    "total_slots": slots,
                    "fast_charger": fast,
                    "power_kw": power,
                },
            )
            if created:
                stations_created += 1
                self.stdout.write(f"  + {name}")
            else:
                stations_skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"  ✓ Stations: {stations_created} created, {stations_skipped} already existed"
            )
        )

        # ── Summary ─────────────────────────────────────────────────────
        total_vehicles = EVVehicle.objects.count()
        total_stations = ChargingStation.objects.count()
        fast_count = ChargingStation.objects.filter(fast_charger=True).count()
        slow_count = total_stations - fast_count

        self.stdout.write(
            self.style.SUCCESS(
                f"\n{'='*55}"
                f"\n  DATABASE SUMMARY"
                f"\n{'='*55}"
                f"\n  Total EV Vehicles  : {total_vehicles}"
                f"\n  Total Stations     : {total_stations}"
                f"\n    ├─ Fast Chargers : {fast_count}"
                f"\n    └─ Slow Chargers : {slow_count}"
                f"\n{'='*55}\n"
            )
        )
