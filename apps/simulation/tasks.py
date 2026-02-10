"""Celery tasks for energy simulation."""

from celery import shared_task
from datetime import datetime
from django.contrib.auth.models import User
from apps.devices.models import Device
from apps.simulation.redis_client import RedisClient
from apps.simulation.simulators.solar import SolarPanelSimulator
from apps.simulation.simulators.generator import GeneratorSimulator
from apps.simulation.simulators.battery import BatterySimulator
from apps.simulation.simulators.ev import EVSimulator
from apps.simulation.simulators.consumption import ConsumptionSimulator


@shared_task
def run_energy_simulation():
    """
    Main orchestrator task that runs every 60 seconds.

    Spawns individual device simulation tasks for all devices.
    """
    devices = Device.objects.select_related(
        'solarpanel', 'generator', 'battery', 'electricvehicle',
        'airconditioner', 'heater', 'user'
    ).all()

    # Spawn simulation task for each device
    for device in devices:
        simulate_device.delay(device.id)

    # Get unique user IDs
    user_ids = devices.values_list('user_id', flat=True).distinct()

    # Compute stats for each user
    for user_id in user_ids:
        compute_user_energy_stats.delay(user_id)


@shared_task
def simulate_device(device_id: int):
    """
    Simulate a single device and store results in Redis.

    Args:
        device_id: The ID of the device to simulate
    """
    try:
        device = Device.objects.select_related(
            'solarpanel', 'generator', 'battery', 'electricvehicle',
            'airconditioner', 'heater'
        ).get(id=device_id)
    except Device.DoesNotExist:
        return

    timestamp = datetime.utcnow()
    redis_client = RedisClient()

    # Get specific device and appropriate simulator
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
        return

    # Run simulation
    result = simulator.simulate(timestamp)

    # Store result in Redis
    if device_type in ['battery', 'electric_vehicle']:
        # Storage devices have different data structure
        storage_data = {
            'capacity_wh': result['capacity_wh'],
            'current_level_wh': result['current_level_wh'],
            'flow_w': result['flow_w'],
            'timestamp': result['timestamp'],
            'status': result['status'],
        }
        # Include mode for EVs
        if device_type == 'electric_vehicle' and 'mode' in result:
            storage_data['mode'] = result['mode']
        redis_client.store_device_storage(device_id, storage_data)
    else:
        # Production and consumption devices
        redis_client.store_device_data(device_id, result)


@shared_task
def compute_user_energy_stats(user_id: int):
    """
    Compute aggregated energy statistics for a user.

    Args:
        user_id: The ID of the user
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return

    devices = Device.objects.filter(user=user).select_related(
        'solarpanel', 'generator', 'battery', 'electricvehicle',
        'airconditioner', 'heater'
    )

    redis_client = RedisClient()

    # Initialize counters
    total_production = 0.0  # Watts
    total_consumption = 0.0  # Watts
    total_storage_capacity = 0.0  # Wh
    total_storage_level = 0.0  # Wh
    total_storage_flow = 0.0  # Watts (+ charging, - discharging)

    for device in devices:
        device_type = device.get_device_type()

        if device_type in ['solar_panel', 'generator']:
            # Production devices
            data = redis_client.get_device_data(device.id)
            if data and data.get('status') == 'online':
                total_production += data.get('power_w', 0.0)

        elif device_type in ['battery', 'electric_vehicle']:
            # Storage devices
            data = redis_client.get_device_storage(device.id)
            if data and data.get('status') == 'online':
                total_storage_capacity += data.get('capacity_wh', 0.0)
                total_storage_level += data.get('current_level_wh', 0.0)
                total_storage_flow += data.get('flow_w', 0.0)

        elif device_type in ['air_conditioner', 'heater']:
            # Consumption devices
            data = redis_client.get_device_data(device.id)
            if data and data.get('status') == 'online':
                total_consumption += data.get('power_w', 0.0)

    # Calculate storage percentage
    storage_percentage = 0.0
    if total_storage_capacity > 0:
        storage_percentage = (total_storage_level / total_storage_capacity) * 100

    # Calculate net grid flow
    # Positive = importing from grid, Negative = exporting to grid
    net_grid_flow = total_consumption + total_storage_flow - total_production

    # Store aggregated stats
    stats = {
        'current_production': total_production,
        'current_consumption': total_consumption,
        'storage': {
            'total_capacity_wh': total_storage_capacity,
            'current_level_wh': total_storage_level,
            'percentage': storage_percentage,
        },
        'current_storage_flow': total_storage_flow,
        'net_grid_flow': net_grid_flow,
        'timestamp': datetime.utcnow().isoformat(),
    }

    redis_client.store_user_stats(user_id, stats)
