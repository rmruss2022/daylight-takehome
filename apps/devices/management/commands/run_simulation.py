"""Management command to manually run simulation once."""
from django.core.management.base import BaseCommand
from datetime import datetime
from django.contrib.auth.models import User
from apps.devices.models import Device
from apps.simulation.redis_client import RedisClient
from apps.simulation.simulators.solar import SolarPanelSimulator
from apps.simulation.simulators.generator import GeneratorSimulator
from apps.simulation.simulators.battery import BatterySimulator
from apps.simulation.simulators.ev import EVSimulator
from apps.simulation.simulators.consumption import ConsumptionSimulator


class Command(BaseCommand):
    help = 'Manually run simulation for all devices and compute stats'

    def handle(self, *args, **options):
        timestamp = datetime.utcnow()
        devices = Device.objects.select_related(
            'solarpanel', 'generator', 'battery', 'electricvehicle',
            'airconditioner', 'heater', 'user'
        ).all()
        
        redis_client = RedisClient()
        
        self.stdout.write(f'Running simulation for {devices.count()} devices...')
        
        success_count = 0
        for device in devices:
            try:
                specific_device = device.get_specific_device()
                device_type = device.get_device_type()
                
                # Instantiate appropriate simulator
                if device_type == 'solar_panel':
                    simulator = SolarPanelSimulator(specific_device)
                elif device_type == 'generator':
                    simulator = GeneratorSimulator(specific_device)
                elif device_type == 'battery':
                    simulator = BatterySimulator(specific_device)
                elif device_type == 'electric_vehicle':
                    simulator = EVSimulator(specific_device)
                elif device_type in ['air_conditioner', 'heater']:
                    simulator = ConsumptionSimulator(specific_device)
                else:
                    continue
                
                # Run simulation
                result = simulator.simulate(timestamp)
                
                # Store result in Redis
                if device_type in ['battery', 'electric_vehicle']:
                    storage_data = {
                        'capacity_wh': result['capacity_wh'],
                        'current_level_wh': result['current_level_wh'],
                        'flow_w': result['flow_w'],
                        'timestamp': result['timestamp'],
                        'status': result['status'],
                    }
                    if device_type == 'electric_vehicle' and 'mode' in result:
                        storage_data['mode'] = result['mode']
                    redis_client.store_device_storage(device.id, storage_data)
                else:
                    redis_client.store_device_data(device.id, result)
                
                power_value = result.get('power_w', result.get('flow_w', 0))
                self.stdout.write(self.style.SUCCESS(
                    f'✅ {device.name} ({device_type}): {power_value:.1f} W'
                ))
                success_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'❌ {device.name}: {str(e)}'
                ))
        
        # Compute user stats
        self.stdout.write('\nComputing user energy stats...')
        user_ids = devices.values_list('user_id', flat=True).distinct()
        
        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                user_devices = Device.objects.filter(user=user)
                
                total_production = 0.0
                total_consumption = 0.0
                total_storage_capacity_wh = 0.0
                total_storage_level_wh = 0.0
                storage_flow = 0.0
                
                for device in user_devices:
                    device_type = device.get_device_type()
                    
                    if device_type in ['battery', 'electric_vehicle']:
                        storage_data = redis_client.get_device_storage(device.id)
                        if storage_data:
                            total_storage_capacity_wh += storage_data.get('capacity_wh', 0)
                            total_storage_level_wh += storage_data.get('current_level_wh', 0)
                            storage_flow += storage_data.get('flow_w', 0)
                    else:
                        device_data = redis_client.get_device_data(device.id)
                        if device_data:
                            power_w = device_data.get('power_w', 0)
                            if device_type in ['solar_panel', 'generator']:
                                total_production += power_w
                            elif device_type in ['air_conditioner', 'heater']:
                                total_consumption += power_w
                
                storage_percentage = (total_storage_level_wh / total_storage_capacity_wh * 100) if total_storage_capacity_wh > 0 else 0
                net_grid_flow = total_consumption - total_production - storage_flow
                
                stats = {
                    'current_production': total_production,
                    'current_consumption': total_consumption,
                    'current_storage': {
                        'total_capacity_wh': total_storage_capacity_wh,
                        'current_level_wh': total_storage_level_wh,
                        'percentage': storage_percentage,
                    },
                    'current_storage_flow': storage_flow,
                    'net_grid_flow': net_grid_flow,
                }
                
                redis_client.store_user_stats(user_id, stats)
                
                self.stdout.write(self.style.SUCCESS(
                    f'✅ {user.username}: Production={total_production:.0f}W, '
                    f'Consumption={total_consumption:.0f}W, Storage={storage_percentage:.1f}%'
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'❌ User {user_id}: {str(e)}'
                ))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n📊 Simulation complete: {success_count}/{devices.count()} devices'
        ))
