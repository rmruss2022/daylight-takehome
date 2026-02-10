"""Tests for device simulators."""

import pytest
from datetime import datetime
from freezegun import freeze_time
from apps.simulation.simulators.solar import SolarPanelSimulator
from apps.simulation.simulators.generator import GeneratorSimulator
from apps.simulation.simulators.battery import BatterySimulator
from apps.simulation.simulators.ev import EVSimulator
from apps.simulation.simulators.consumption import ConsumptionSimulator
from apps.devices.models import EVMode


@pytest.mark.django_db
class TestSolarPanelSimulator:
    """Test solar panel simulator."""

    @freeze_time("2024-06-21 20:00:00")  # Summer solstice, solar noon in SF (UTC time)
    def test_solar_output_at_noon(self, solar_panel):
        """Test solar output at noon (should be high)."""
        simulator = SolarPanelSimulator(solar_panel)
        result = simulator.simulate(datetime.utcnow())

        assert result['power_w'] > 0
        assert result['power_w'] <= solar_panel.max_capacity_w
        assert result['status'] == 'online'

    @freeze_time("2024-06-21 10:00:00")  # Night in SF (UTC time)
    def test_solar_output_at_night(self, solar_panel):
        """Test solar output at night (should be zero)."""
        simulator = SolarPanelSimulator(solar_panel)
        result = simulator.simulate(datetime.utcnow())

        assert result['power_w'] == 0
        assert result['status'] == 'online'

    @freeze_time("2024-06-21 08:00:00")  # Morning
    def test_solar_output_in_morning(self, solar_panel):
        """Test solar output in morning (should be moderate)."""
        simulator = SolarPanelSimulator(solar_panel)
        result = simulator.simulate(datetime.utcnow())

        assert result['power_w'] >= 0
        assert result['power_w'] <= solar_panel.max_capacity_w

    def test_solar_output_offline_device(self, solar_panel):
        """Test solar panel when offline."""
        solar_panel.status = 'offline'
        solar_panel.save()

        simulator = SolarPanelSimulator(solar_panel)
        result = simulator.simulate(datetime.utcnow())

        assert result['power_w'] == 0


@pytest.mark.django_db
class TestGeneratorSimulator:
    """Test generator simulator."""

    def test_generator_output_with_variation(self, generator):
        """Test generator produces output with variation."""
        simulator = GeneratorSimulator(generator)

        # Run multiple simulations to check variation
        outputs = []
        for _ in range(10):
            result = simulator.simulate(datetime.utcnow())
            outputs.append(result['power_w'])

        # Should be around rated output (±5%)
        for output in outputs:
            assert 2850 <= output <= 3150  # 3000 ± 5%

        # Should have some variation
        assert len(set(outputs)) > 1

    def test_generator_offline(self, generator):
        """Test generator when offline."""
        generator.status = 'offline'
        generator.save()

        simulator = GeneratorSimulator(generator)
        result = simulator.simulate(datetime.utcnow())

        assert result['power_w'] == 0


@pytest.mark.django_db
class TestBatterySimulator:
    """Test battery simulator."""

    def test_battery_charges_when_low(self, battery):
        """Test battery charges when below 50%."""
        battery.current_charge_kwh = 3.0  # 30%
        battery.save()

        simulator = BatterySimulator(battery)
        result = simulator.simulate(datetime.utcnow())

        assert result['flow_w'] > 0  # Positive = charging
        assert result['current_level_wh'] >= 3000  # Should increase

    def test_battery_discharges_when_high(self, battery):
        """Test battery discharges when above 70%."""
        battery.current_charge_kwh = 8.0  # 80%
        battery.save()

        simulator = BatterySimulator(battery)
        result = simulator.simulate(datetime.utcnow())

        assert result['flow_w'] < 0  # Negative = discharging

    def test_battery_respects_capacity(self, battery):
        """Test battery doesn't exceed capacity."""
        battery.current_charge_kwh = 9.9
        battery.save()

        simulator = BatterySimulator(battery)
        result = simulator.simulate(datetime.utcnow())

        assert result['current_level_wh'] <= 10000  # Won't exceed capacity


@pytest.mark.django_db
class TestEVSimulator:
    """Test EV simulator."""

    @freeze_time("2024-01-15 10:00:00")  # Monday 10 AM - should be away
    def test_ev_away_during_weekday(self, electric_vehicle):
        """Test EV is offline during weekday work hours."""
        simulator = EVSimulator(electric_vehicle)
        result = simulator.simulate(datetime.utcnow())

        electric_vehicle.refresh_from_db()
        assert electric_vehicle.mode == EVMode.OFFLINE

    @freeze_time("2024-01-15 20:00:00")  # Monday 8 PM - should be home
    def test_ev_home_in_evening(self, electric_vehicle):
        """Test EV is charging in the evening."""
        electric_vehicle.current_charge_kwh = 30.0  # Below 90%
        electric_vehicle.save()

        simulator = EVSimulator(electric_vehicle)
        result = simulator.simulate(datetime.utcnow())

        electric_vehicle.refresh_from_db()
        assert electric_vehicle.mode == EVMode.CHARGING
        assert result['flow_w'] > 0  # Charging

    @freeze_time("2024-01-20 10:00:00")  # Saturday 10 AM - should be home
    def test_ev_home_on_weekend(self, electric_vehicle):
        """Test EV is home on weekend."""
        electric_vehicle.current_charge_kwh = 30.0
        electric_vehicle.save()

        simulator = EVSimulator(electric_vehicle)
        result = simulator.simulate(datetime.utcnow())

        electric_vehicle.refresh_from_db()
        assert electric_vehicle.mode == EVMode.CHARGING


@pytest.mark.django_db
class TestConsumptionSimulator:
    """Test consumption device simulator."""

    def test_consumption_within_range(self, air_conditioner):
        """Test consumption stays within min/max range."""
        simulator = ConsumptionSimulator(air_conditioner)

        # Run multiple times to check variation
        for _ in range(10):
            result = simulator.simulate(datetime.utcnow())
            assert air_conditioner.min_power_w <= result['power_w'] <= air_conditioner.max_power_w

    def test_consumption_offline(self, air_conditioner):
        """Test consumption device when offline."""
        air_conditioner.status = 'offline'
        air_conditioner.save()

        simulator = ConsumptionSimulator(air_conditioner)
        result = simulator.simulate(datetime.utcnow())

        assert result['power_w'] == 0
