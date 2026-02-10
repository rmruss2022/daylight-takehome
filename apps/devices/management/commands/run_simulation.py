"""Management command to manually run simulation once."""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.devices.models import Device
from apps.simulation.tasks import simulate_device


class Command(BaseCommand):
    help = 'Manually run simulation for all online devices'

    def handle(self, *args, **options):
        timestamp = timezone.now()
        devices = Device.objects.filter(status='online')
        
        self.stdout.write(f'Running simulation for {devices.count()} online devices...')
        
        success_count = 0
        for device in devices:
            try:
                # Run simulation directly (not async)
                from apps.simulation.simulators import get_simulator
                simulator = get_simulator(device)
                if simulator:
                    data = simulator.simulate(timestamp)
                    
                    # Store in Redis
                    from apps.devices.utils.redis_client import RedisClient
                    redis_client = RedisClient()
                    redis_client.set_device_data(device.id, data)
                    
                    self.stdout.write(self.style.SUCCESS(
                        f'✅ {device.name}: {data.get("power_w", 0):.1f} W'
                    ))
                    success_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'❌ {device.name}: {str(e)}'
                ))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n📊 Simulation complete: {success_count}/{devices.count()} devices'
        ))
