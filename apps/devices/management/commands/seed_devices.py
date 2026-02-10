"""Management command to seed database with sample devices."""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.devices.models import (
    SolarPanel, Generator, Battery, ElectricVehicle,
    AirConditioner, Heater
)


class Command(BaseCommand):
    help = 'Seed database with sample devices for testing'

    def handle(self, *args, **options):
        # Create test users
        user1, created = User.objects.get_or_create(
            username='testuser1',
            defaults={
                'email': 'testuser1@example.com',
                'first_name': 'Test',
                'last_name': 'User One'
            }
        )
        if created:
            user1.set_password('testpass123')
            user1.save()
            self.stdout.write(self.style.SUCCESS(f'Created user: {user1.username}'))

        user2, created = User.objects.get_or_create(
            username='testuser2',
            defaults={
                'email': 'testuser2@example.com',
                'first_name': 'Test',
                'last_name': 'User Two'
            }
        )
        if created:
            user2.set_password('testpass123')
            user2.save()
            self.stdout.write(self.style.SUCCESS(f'Created user: {user2.username}'))

        # Create devices for user1
        devices_created = 0

        # Solar Panels
        if not SolarPanel.objects.filter(user=user1, name='Rooftop Solar Array').exists():
            SolarPanel.objects.create(
                user=user1,
                name='Rooftop Solar Array',
                panel_area_m2=25.0,
                efficiency=0.20,
                max_capacity_w=5000.0,
                latitude=37.77,
                longitude=-122.42,
            )
            devices_created += 1

        # Generator
        if not Generator.objects.filter(user=user1, name='Backup Generator').exists():
            Generator.objects.create(
                user=user1,
                name='Backup Generator',
                rated_output_w=3000.0,
            )
            devices_created += 1

        # Battery
        if not Battery.objects.filter(user=user1, name='Home Battery Pack').exists():
            Battery.objects.create(
                user=user1,
                name='Home Battery Pack',
                capacity_kwh=13.5,
                current_charge_kwh=6.75,
                max_charge_rate_kw=5.0,
                max_discharge_rate_kw=5.0,
            )
            devices_created += 1

        # Electric Vehicle
        if not ElectricVehicle.objects.filter(user=user1, name='Tesla Model 3').exists():
            ElectricVehicle.objects.create(
                user=user1,
                name='Tesla Model 3',
                capacity_kwh=75.0,
                current_charge_kwh=45.0,
                max_charge_rate_kw=11.0,
                max_discharge_rate_kw=7.0,
                mode='charging',
                driving_efficiency_kwh_per_hour=3.0,
            )
            devices_created += 1

        # Air Conditioner
        if not AirConditioner.objects.filter(user=user1, name='Central AC').exists():
            AirConditioner.objects.create(
                user=user1,
                name='Central AC',
                rated_power_w=3500.0,
                min_power_w=1500.0,
                max_power_w=4500.0,
            )
            devices_created += 1

        # Heater
        if not Heater.objects.filter(user=user1, name='Electric Heater').exists():
            Heater.objects.create(
                user=user1,
                name='Electric Heater',
                rated_power_w=2000.0,
                min_power_w=800.0,
                max_power_w=2500.0,
            )
            devices_created += 1

        # Create some devices for user2
        if not SolarPanel.objects.filter(user=user2, name='Small Solar Panel').exists():
            SolarPanel.objects.create(
                user=user2,
                name='Small Solar Panel',
                panel_area_m2=10.0,
                efficiency=0.18,
                max_capacity_w=1800.0,
                latitude=37.77,
                longitude=-122.42,
            )
            devices_created += 1

        if not Battery.objects.filter(user=user2, name='Compact Battery').exists():
            Battery.objects.create(
                user=user2,
                name='Compact Battery',
                capacity_kwh=5.0,
                current_charge_kwh=2.5,
                max_charge_rate_kw=2.0,
                max_discharge_rate_kw=2.0,
            )
            devices_created += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {devices_created} devices')
        )
        self.stdout.write(
            self.style.SUCCESS('Test credentials: testuser1 / testpass123')
        )
