# Smart Home Energy Management System

A Dockerized Django GraphQL API backend for managing smart home energy devices with real-time energy statistics and simulation.

## Features

- **Device Management**: Solar panels, generators, batteries, electric vehicles, air conditioners, and heaters
- **Real-time Energy Statistics**: Production, consumption, storage, and grid flow monitoring
- **Realistic Simulation**: Celery-powered background tasks simulate device behavior
- **GraphQL API**: Modern API with Strawberry GraphQL
- **JWT Authentication**: Secure user authentication
- **Django Admin**: Full admin interface for device management

## Quick Start

**For detailed step-by-step instructions, see [QUICKSTART.md](QUICKSTART.md)**

### Prerequisites

- Docker and Docker Compose
- Git

### Installation (Using Makefile)

```bash
# First time setup
make setup

# Create admin user
make createsuperuser

# Load sample data
make seed

# Visit http://localhost:8000/graphql
```

### Installation (Manual)

1. Clone the repository:
```bash
git clone <repository-url>
cd Daylight
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Build and start services:
```bash
docker-compose up --build
```

This will start:
- `web`: Django application (port 8000)
- `db`: PostgreSQL database (port 5432)
- `redis`: Redis cache (port 6379)
- `celery`: Celery worker
- `celery-beat`: Celery scheduler (runs simulation every 60s)

4. In a new terminal, run migrations:
```bash
docker-compose exec web python manage.py migrate
```

5. Create a superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

6. (Optional) Seed test data:
```bash
docker-compose exec web python manage.py seed_devices
```

This creates two test users with sample devices:
- Username: `testuser1`, Password: `testpass123`
- Username: `testuser2`, Password: `testpass123`

### Access the Application

- **GraphQL Playground**: http://localhost:8000/graphql
- **Django Admin**: http://localhost:8000/admin
- **Health Check**: http://localhost:8000/health

## API Usage

### Authentication

First, obtain a JWT token:

```graphql
mutation Login {
  loginUser(username: "testuser1", password: "testpass123") {
    token
    user {
      id
      username
      email
    }
  }
}
```

Add the token to subsequent requests in the `Authorization` header:
```
Authorization: Bearer <your-token-here>
```

### Query All Devices

```graphql
query GetDevices {
  allDevices {
    ... on SolarPanelType {
      id
      name
      status
      panelAreaM2
      efficiency
      maxCapacityW
    }
    ... on BatteryType {
      id
      name
      status
      capacityKwh
      currentChargeKwh
      chargePercentage
    }
    ... on ElectricVehicleType {
      id
      name
      status
      mode
      capacityKwh
      currentChargeKwh
      chargePercentage
    }
  }
}
```

### Get Energy Statistics

```graphql
query GetEnergyStats {
  energyStats {
    currentProduction
    currentConsumption
    currentStorage {
      totalCapacityWh
      currentLevelWh
      percentage
    }
    currentStorageFlow
    netGridFlow
  }
}
```

### Create a Device

```graphql
mutation CreateSolarPanel {
  createDevice(input: {
    name: "Rooftop Solar"
    deviceType: SOLAR_PANEL
    panelAreaM2: 20.0
    efficiency: 0.20
    maxCapacityW: 4000.0
    latitude: 37.77
    longitude: -122.42
  }) {
    ... on SolarPanelType {
      id
      name
      maxCapacityW
    }
  }
}
```

### Update a Device

```graphql
mutation UpdateDevice {
  updateDevice(id: 1, input: {
    name: "Updated Name"
    status: OFFLINE
  }) {
    ... on SolarPanelType {
      id
      name
      status
    }
  }
}
```

## System Architecture

### Data Model

The system uses Django's Multi-Table Inheritance with a base `Device` model and specialized models for each device type:

- **Production**: `SolarPanel`, `Generator`
- **Storage**: `Battery`, `ElectricVehicle`
- **Consumption**: `AirConditioner`, `Heater`

Electric Vehicles have dual functionality (charging/discharging) managed through a `mode` field.

### Simulation Pipeline

1. **Celery Beat** triggers `run_energy_simulation` every 60 seconds
2. **Orchestrator** spawns `simulate_device` task for each device
3. **Simulators** compute realistic energy values:
   - Solar panels: Solar elevation angle based on time/location
   - Generators: Steady output with ±5% variation
   - Batteries: Charge/discharge with C-rate limits
   - EVs: Connection schedule (away 7 AM - 6 PM weekdays)
   - Consumption: Variable wattage within min/max range
4. **Results** stored in Redis with 60s TTL
5. **Aggregator** computes user-level statistics
6. **GraphQL** `energyStats` query reads from Redis

### Redis Key Schema

```
device:{device_id}:current       # Device power output/consumption
device:{device_id}:storage       # Storage device state
device:{device_id}:last_seen     # EV offline tracking
user:{user_id}:energy_stats      # Aggregated user statistics
```

## Development

### Running Tests

```bash
docker-compose exec web pytest
```

With coverage:
```bash
docker-compose exec web pytest --cov=apps --cov-report=html
```

### Database Management

Reset database:
```bash
docker-compose down -v
docker-compose up -d db
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### Accessing Services

Django shell:
```bash
docker-compose exec web python manage.py shell
```

Redis CLI:
```bash
docker-compose exec redis redis-cli
```

PostgreSQL:
```bash
docker-compose exec db psql -U postgres -d smart_home_energy
```

View Celery logs:
```bash
docker-compose logs -f celery
docker-compose logs -f celery-beat
```

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Enable/disable debug mode
- `POSTGRES_*`: Database configuration
- `REDIS_URL`: Redis connection URL
- `JWT_SECRET_KEY`: JWT signing key
- `JWT_EXPIRY_HOURS`: Token expiration time

## Device Specifications

### Solar Panel
- Uses solar elevation angle calculation
- Clear-sky irradiance model
- Default location: San Francisco (37.77°N, 122.42°W)
- Zero output at night
- Random cloud cover variation (85-100%)

### Electric Vehicle
- **Away Schedule**: 7 AM - 6 PM on weekdays
- **Driving Consumption**: 3 kWh/hour (configurable)
- **Charge Target**: 90% capacity
- **Modes**: Charging, Discharging, Offline

### Battery
- **Charge Logic**: Charge if below 50%
- **Discharge Logic**: Discharge if above 70%
- **Idle**: Between 50-70%

## Troubleshooting

### Simulation not running

Check Celery Beat is running:
```bash
docker-compose logs celery-beat
```

Manually trigger simulation:
```bash
docker-compose exec web python manage.py shell
>>> from apps.simulation.tasks import run_energy_simulation
>>> run_energy_simulation.delay()
```

### No energy stats returned

Wait at least 60 seconds after starting for first simulation to run, or check Redis:
```bash
docker-compose exec redis redis-cli
127.0.0.1:6379> KEYS user:*
127.0.0.1:6379> GET user:1:energy_stats
```

### GraphQL permission errors

Ensure you're sending the JWT token in the Authorization header:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## Design Documentation

See [DESIGN.md](DESIGN.md) for detailed architecture decisions, scaling considerations, and implementation rationale.

## License

This project is a technical assessment implementation.
