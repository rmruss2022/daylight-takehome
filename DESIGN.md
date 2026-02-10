# Design Documentation

## Architecture Overview

This document explains the key design decisions, trade-offs, and implementation details of the Smart Home Energy Management System.

## Data Model Design

### Choice: Multi-Table Inheritance (MTI)

**Selected Approach**: Django's Multi-Table Inheritance with concrete `Device` base model

**Rationale**:
- **Type-specific fields**: Each device type has unique attributes (e.g., `panel_area_m2` for solar panels, `mode` for EVs) without sparse columns
- **Polymorphic queries**: Can query all devices with `Device.objects.all()` or specific types with `SolarPanel.objects.all()`
- **GraphQL compatibility**: Works naturally with GraphQL unions and interfaces
- **EV dual-role**: Electric vehicles handled elegantly with single model + `mode` field instead of complex dual inheritance

**Alternatives Considered**:
1. **Single Table Inheritance (Abstract Base)**: Rejected due to inability to query across all devices polymorphically
2. **Separate tables with no inheritance**: Rejected due to code duplication and complex multi-type queries
3. **Generic Foreign Keys**: Rejected due to loss of referential integrity and poor performance

**Structure**:
```
Device (base)
├── SolarPanel
├── Generator
├── Battery
├── ElectricVehicle (with mode: charging/discharging/offline)
├── AirConditioner
└── Heater
```

### Electric Vehicle Dual-Role Design

**Challenge**: EVs act as both consumption devices (when charging) and storage devices (when discharging via V2H).

**Solution**: Single `ElectricVehicle` model with `mode` field:
- `CHARGING`: Drawing power from the grid/home
- `DISCHARGING`: Supplying power to home (V2H)
- `OFFLINE`: Disconnected (driving)

**Benefits**:
- Single source of truth for EV state
- Simplified simulation logic
- Accurate offline tracking with `last_seen_at` timestamp
- Natural state transitions

## GraphQL Library Selection

### Choice: Strawberry Django

**Selected**: Strawberry Django over Graphene-Django

**Rationale**:
- **Modern syntax**: Decorator-based with Python type hints (similar to FastAPI)
- **Type safety**: Full IDE support with mypy compatibility
- **Active development**: More frequent updates than Graphene
- **Django integration**: Better ORM optimization and built-in Django features
- **Async support**: Ready for async Django views when needed

**Example Comparison**:
```python
# Strawberry (selected)
@strawberry.type
class SolarPanelType:
    id: int
    name: str
    max_capacity_w: float

# Graphene (alternative)
class SolarPanelType(DjangoObjectType):
    class Meta:
        model = SolarPanel
        fields = ['id', 'name', 'max_capacity_w']
```

## Simulation Architecture

### Pipeline Design

**Flow**:
1. Celery Beat triggers `run_energy_simulation` every 60 seconds
2. Orchestrator spawns individual `simulate_device` tasks
3. Each simulator computes realistic values
4. Results stored in Redis with 60s TTL
5. `compute_user_energy_stats` aggregates per user
6. GraphQL queries read from Redis

**Key Decisions**:

**Why Redis over Database?**
- Fast read/write for high-frequency updates (60s intervals)
- Automatic expiration with TTL
- Reduced database load
- Acceptable data loss risk (simulation regenerates every 60s)

**Why Celery Task per Device?**
- Parallelization: Devices simulate concurrently
- Fault isolation: One device failure doesn't break entire simulation
- Scalability: Easy to distribute across workers

**Why 60-second interval?**
- Balance between real-time feel and resource usage
- Solar elevation changes meaningfully over 1 minute
- Battery/EV charge updates are realistic at this granularity

### Redis Key Schema

```
device:{device_id}:current = {
    "power_w": 1500,
    "timestamp": "2024-01-15T12:00:00",
    "status": "online"
}

device:{device_id}:storage = {
    "capacity_wh": 75000,
    "current_level_wh": 45000,
    "flow_w": -500  # negative = discharging
}

user:{user_id}:energy_stats = {
    "current_production": 5000,
    "current_consumption": 3500,
    "net_grid_flow": -1500  # negative = exporting
}
```

**TTL Strategy**:
- Device data: 60 seconds (matches simulation interval)
- User stats: 60 seconds
- EV last_seen: 24 hours (for offline tracking)

## Solar Panel Simulation

### Clear-Sky Irradiance Model

**Approach**: Solar elevation angle calculation using latitude, longitude, and time

**Formula**:
```python
elevation_angle = arcsin(
    sin(latitude) * sin(declination) +
    cos(latitude) * cos(declination) * cos(hour_angle)
)

irradiance = 1000 W/m² * sin(elevation) * atmospheric_attenuation
power = irradiance * panel_area * efficiency * cloud_factor
```

**Assumptions**:
- Clear-sky model (simplified, no weather API)
- Default location: San Francisco (37.77°N, 122.42°W)
- Atmospheric attenuation: 0.7^(air_mass - 1)
- Cloud cover: Random 0.85-1.0 multiplier
- Zero output when elevation ≤ 0° (night)

**Why This Model?**
- No external API dependencies (free, no rate limits)
- Physically realistic (follows solar geometry)
- Time-zone aware
- Good enough for demonstration purposes

**Alternatives Considered**:
1. **Weather API (OpenWeatherMap)**: Rejected due to API costs and rate limits
2. **Historical solar data**: Rejected due to complexity and storage requirements
3. **Fixed pattern**: Rejected as too simplistic and not time-accurate

### Solar Declination Calculation

```python
# Day 81 is vernal equinox (March 21)
declination = 23.45° * sin((360/365) * (day_of_year - 81))
```

Varies from -23.45° (winter solstice) to +23.45° (summer solstice).

## Electric Vehicle Connection Schedule

### Schedule Logic

**Schedule**: Away 7 AM - 6 PM on weekdays, connected otherwise

**Implementation**:
```python
is_weekday = timestamp.weekday() < 5  # Monday=0, Friday=4
hour = timestamp.hour
should_be_away = is_weekday and 7 <= hour < 18
```

**State Management**:

When away (offline):
1. Set `mode = OFFLINE`
2. Store `last_seen_at = current_time`
3. Calculate driving consumption: `energy_consumed = driving_efficiency * hours_away`
4. Deduct from `current_charge_kwh`

When connected:
1. Calculate missed driving time
2. Deduct accumulated consumption
3. Set `mode = CHARGING`
4. Charge until 90% capacity
5. Update `last_seen_at`

**Why This Design?**
- Realistic commute pattern
- Demonstrates offline state tracking
- Shows charge level changes even when disconnected
- Tests boundary conditions (connection/disconnection)

**Hardcoded Schedule Trade-off**:
- **Pro**: Simple, predictable, easy to test
- **Con**: Not customizable per vehicle
- **Future**: Could add schedule fields to model

## Authentication Design

### JWT Token Strategy

**Flow**:
1. User calls `loginUser(username, password)`
2. Django authenticates via `authenticate()`
3. Generate JWT with user_id, expiry
4. Client includes token in `Authorization: Bearer <token>`
5. `IsAuthenticated` permission class validates token

**Token Payload**:
```json
{
  "user_id": 1,
  "username": "testuser1",
  "exp": 1642252800,  # 24 hours from issue
  "iat": 1642166400
}
```

**Why JWT over Sessions?**
- Stateless (no session storage)
- Works with mobile/SPA clients
- Easy to scale horizontally
- Standard for GraphQL APIs

**Security Considerations**:
- Short expiry (24 hours)
- HTTPS required in production
- Secret key must be environment variable
- No token refresh implemented (future enhancement)

## Energy Statistics Calculation

### Net Grid Flow Formula

```python
net_grid_flow = consumption + storage_flow - production

# Examples:
# consumption=3000W, storage_flow=500W (charging), production=2000W
# net_grid_flow = 3000 + 500 - 2000 = 1500W (importing)

# consumption=1000W, storage_flow=-500W (discharging), production=3000W
# net_grid_flow = 1000 - 500 - 3000 = -2500W (exporting)
```

**Sign Convention**:
- `net_grid_flow > 0`: Importing from grid
- `net_grid_flow < 0`: Exporting to grid
- `storage_flow > 0`: Charging (consuming power)
- `storage_flow < 0`: Discharging (producing power)

## Scaling Considerations

### Current System Capacity

**At 10,000 users × 50 devices (500,000 devices)**:

**Bottlenecks**:
1. **Celery Task Queue**:
   - 500K tasks every 60 seconds = ~8,333 tasks/second
   - Single worker processes ~10-50 tasks/second
   - **Solution**: Horizontal scaling with 100-200 Celery workers

2. **Redis Memory**:
   - ~1KB per device × 500K = 500 MB
   - ~2KB per user × 10K = 20 MB
   - **Total**: ~520 MB (well within Redis capacity)

3. **Database Queries**:
   - 500K device lookups every 60 seconds
   - **Solution**: Read replicas, connection pooling, select_related optimization

4. **GraphQL Queries**:
   - Potentially 10K concurrent `energyStats` queries
   - **Solution**: Redis caching (already implemented), CDN for static schema

### Scaling Solutions

**Horizontal Scaling**:
```yaml
# docker-compose.production.yml
celery:
  deploy:
    replicas: 100  # Scale workers

redis:
  image: redis/redis-stack-server  # Redis Cluster

db:
  # Add read replicas
```

**Batch Processing**:
Instead of one task per device, batch by user:
```python
@shared_task
def simulate_user_devices(user_id):
    devices = Device.objects.filter(user_id=user_id)
    for device in devices:
        # Simulate in-process
```

**Optimization**:
- Database: Index on `(user_id, status)`, `created_at`
- Redis: Use pipelining for bulk writes
- Celery: Use `rate_limit` to prevent thundering herd
- GraphQL: Add DataLoader for N+1 query prevention

## Known Limitations

### 1. Solar Model Simplifications

**Limitations**:
- No cloud cover (only random variation)
- No temperature effects on efficiency
- Simplified atmospheric attenuation
- No seasonal shading/tilt optimization

**Impact**: Solar output may be 10-20% optimistic compared to real-world

**Mitigation**: Adequate for demonstration; production would integrate weather API

### 2. EV Schedule Hardcoding

**Limitation**: All EVs use same 7 AM - 6 PM weekday schedule

**Impact**: Unrealistic for shift workers, weekend commuters

**Future**: Add custom schedule fields to `ElectricVehicle` model

### 3. No Historical Data

**Limitation**: Only current state stored (last 60 seconds)

**Impact**: Cannot query past energy usage or trends

**Future**: Add time-series database (InfluxDB, TimescaleDB)

### 4. No Device Control

**Limitation**: Read-only API (no device commands)

**Impact**: Cannot turn devices on/off, set charge limits, etc.

**Future**: Add `deviceCommand` mutation for control signals

### 5. Simulation Drift

**Limitation**: If Celery Beat stops, simulation pauses

**Impact**: Energy stats become stale (Redis TTL expires)

**Mitigation**: Health checks, alerting on Celery failures

### 6. No Real-time Updates

**Limitation**: Clients must poll every 60s

**Impact**: Not truly "real-time"

**Future**: Add GraphQL subscriptions over WebSocket

## Testing Strategy

### Unit Tests

**Models**:
- Device creation and validation
- EV state transitions
- Battery charge clamping

**Simulators**:
- Solar output at different times (using `freezegun`)
- Generator variance within ±5%
- Battery respects C-rate limits
- EV follows schedule

**API**:
- Authentication (valid/invalid credentials)
- Permission checks
- Device CRUD operations

### Integration Tests

**Full Pipeline**:
1. Create devices
2. Run `run_energy_simulation` (with `CELERY_TASK_ALWAYS_EAGER=True`)
3. Check Redis contains data
4. Query `energyStats`
5. Verify calculations

**Multi-User Isolation**:
- User1 cannot see User2 devices
- Stats aggregated separately

### Time-Based Testing

Using `freezegun` to test time-dependent behavior:
```python
from freezegun import freeze_time

@freeze_time("2024-01-15 12:00:00")  # Solar noon
def test_solar_output_at_noon():
    result = simulator.simulate(datetime.utcnow())
    assert result['power_w'] > 0

@freeze_time("2024-01-15 02:00:00")  # Night
def test_solar_output_at_night():
    result = simulator.simulate(datetime.utcnow())
    assert result['power_w'] == 0

@freeze_time("2024-01-15 10:00:00")  # Monday 10 AM
def test_ev_away_during_weekday():
    result = simulator.simulate(datetime.utcnow())
    assert result['mode'] == EVMode.OFFLINE
```

## Performance Benchmarks

**Target Metrics**:
- Simulation cycle: < 60 seconds for 10K devices
- GraphQL `energyStats` query: < 100ms
- Device creation: < 50ms
- Redis round-trip: < 5ms

**Monitoring**:
- Celery task duration (StatsD)
- Redis hit rate
- GraphQL query performance (Apollo Server metrics)
- Database query counts (Django Debug Toolbar)

## Future Enhancements

### Phase 2 Features

1. **Historical Analytics**:
   - Store hourly snapshots in TimescaleDB
   - Energy cost calculations
   - Usage trends and predictions

2. **Device Control**:
   - Turn devices on/off
   - Set battery charge/discharge rates
   - Configure EV departure/arrival times

3. **Real-time Updates**:
   - GraphQL subscriptions
   - WebSocket for live stats
   - Push notifications on anomalies

4. **Advanced Simulation**:
   - Weather API integration
   - Machine learning for load prediction
   - Dynamic battery optimization (peak shaving)

5. **Multi-Home Support**:
   - Users can have multiple locations
   - Aggregate across homes
   - Home-to-home energy sharing

## Conclusion

This design prioritizes:
- **Correctness**: Realistic simulation with physical constraints
- **Scalability**: Redis + Celery architecture can handle growth
- **Maintainability**: Clear separation of concerns (models, API, simulation)
- **Testability**: Deterministic simulators with time mocking
- **Developer Experience**: Modern tools (Strawberry, Docker, pytest)

Trade-offs were made to deliver a working system within time constraints while maintaining production-readiness for the core features.
