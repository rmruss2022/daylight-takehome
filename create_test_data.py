#!/usr/bin/env python
"""Create test user and devices for production database."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.devices.models import Battery, ElectricVehicle, SolarPanel, AirConditioner, Generator

# Create testuser1 if doesn't exist
user, created = User.objects.get_or_create(
    username='testuser1',
    defaults={'email': 'testuser1@example.com', 'is_active': True}
)
if created:
    user.set_password('testpass123')
    user.save()
    print(f"✅ Created user: {user.username}")
else:
    # Update password in case it changed
    user.set_password('testpass123')
    user.save()
    print(f"ℹ️  User already exists: {user.username} (password updated)")

# Create devices for testuser1
devices_created = 0

# Battery 1
battery1, created = Battery.objects.get_or_create(
    name="Home Battery",
    user=user,
    defaults={
        'capacity_kwh': 13.5,
        'current_charge_kwh': 6.75,
        'max_charge_rate_kw': 5.0,
        'max_discharge_rate_kw': 5.0,
        'status': 'online'
    }
)
if created:
    devices_created += 1
    print(f"✅ Created: {battery1.name}")

# Battery 2
battery2, created = Battery.objects.get_or_create(
    name="Garage Battery",
    user=user,
    defaults={
        'capacity_kwh': 10.0,
        'current_charge_kwh': 5.0,
        'max_charge_rate_kw': 3.3,
        'max_discharge_rate_kw': 3.3,
        'status': 'online'
    }
)
if created:
    devices_created += 1
    print(f"✅ Created: {battery2.name}")

# EV
ev, created = ElectricVehicle.objects.get_or_create(
    name="Tesla Model 3",
    user=user,
    defaults={
        'capacity_kwh': 75.0,
        'current_charge_kwh': 64.5,
        'max_charge_rate_kw': 11.0,
        'driving_efficiency_kwh_per_hour': 15.0,
        'status': 'online',
        'mode': 'offline'  # 12:38 PM EST = 5:38 PM UTC, should be driving (7 AM-6 PM EST = 12 PM-11 PM UTC)
    }
)
if created:
    devices_created += 1
    print(f"✅ Created: {ev.name}")

# Solar Panel 1
solar1, created = SolarPanel.objects.get_or_create(
    name="Roof Solar Array",
    user=user,
    defaults={
        'rated_power_kw': 8.0,
        'efficiency': 0.20,
        'azimuth': 180,
        'tilt': 30,
        'status': 'online'
    }
)
if created:
    devices_created += 1
    print(f"✅ Created: {solar1.name}")

# Solar Panel 2
solar2, created = SolarPanel.objects.get_or_create(
    name="Backyard Solar",
    user=user,
    defaults={
        'rated_power_kw': 4.0,
        'efficiency': 0.18,
        'azimuth': 180,
        'tilt': 25,
        'status': 'online'
    }
)
if created:
    devices_created += 1
    print(f"✅ Created: {solar2.name}")

# Air Conditioner
ac, created = AirConditioner.objects.get_or_create(
    name="Central AC",
    user=user,
    defaults={
        'rated_power_kw': 3.5,
        'status': 'online'
    }
)
if created:
    devices_created += 1
    print(f"✅ Created: {ac.name}")

# Generator
gen, created = Generator.objects.get_or_create(
    name="Backup Generator",
    user=user,
    defaults={
        'rated_power_kw': 10.0,
        'fuel_type': 'natural_gas',
        'status': 'offline'
    }
)
if created:
    devices_created += 1
    print(f"✅ Created: {gen.name}")

print(f"\n📊 Summary:")
print(f"  - New devices created: {devices_created}")
print(f"  - Total devices for testuser1: {user.device_set.count()}")
print(f"\n🔑 Login credentials:")
print(f"  - Username: testuser1")
print(f"  - Password: testpass123")
