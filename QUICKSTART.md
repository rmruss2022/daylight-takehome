# Quick Start Guide

This guide will get you up and running with the Smart Home Energy Management System in minutes.

## Prerequisites

- Docker Desktop installed and running
- At least 4GB RAM available
- Ports 8000, 5432, 6379 available

## Installation Steps

### 1. Start the System

```bash
# Start all services (this will take a few minutes on first run)
docker compose up --build
```

Wait until you see messages like:
```
web-1          | Starting development server at http://0.0.0.0:8000/
celery-beat-1  | celery beat v5.4.0 is starting.
celery-1       | celery@xxx ready.
```

### 2. Initialize Database (New Terminal)

Open a new terminal and run:

```bash
# Run database migrations
docker compose exec web python manage.py migrate

# Create a superuser account
docker compose exec web python manage.py createsuperuser
# Enter username, email, and password when prompted

# (Optional) Load sample data
docker compose exec web python manage.py seed_devices
```

### 3. Access the Application

- **GraphQL Playground**: http://localhost:8000/graphql
- **Django Admin**: http://localhost:8000/admin
- **Health Check**: http://localhost:8000/health

## First API Request

### 1. Login and Get Token

In the GraphQL playground (http://localhost:8000/graphql):

```graphql
mutation {
  loginUser(username: "testuser1", password: "testpass123") {
    token
    user {
      id
      username
    }
  }
}
```

Copy the token from the response.

### 2. Set Authorization Header

Click "Headers" at the bottom of the GraphQL playground and add:

```json
{
  "Authorization": "Bearer YOUR_TOKEN_HERE"
}
```

### 3. Query Your Devices

```graphql
query {
  allDevices {
    ... on SolarPanelType {
      id
      name
      maxCapacityW
      status
    }
    ... on BatteryType {
      id
      name
      capacityKwh
      chargePercentage
    }
    ... on ElectricVehicleType {
      id
      name
      mode
      chargePercentage
    }
  }
}
```

### 4. Get Energy Statistics

Wait 60 seconds for the simulation to run, then:

```graphql
query {
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

**Understanding the Response**:
- `currentProduction`: Total watts being generated (solar + generator)
- `currentConsumption`: Total watts being consumed (AC + heater)
- `currentStorageFlow`: Positive = charging batteries, Negative = discharging
- `netGridFlow`: Positive = importing from grid, Negative = exporting to grid

### 5. Create a New Device

```graphql
mutation {
  createDevice(input: {
    name: "My Solar Panel"
    deviceType: SOLAR_PANEL
    panelAreaM2: 15.0
    efficiency: 0.18
    maxCapacityW: 2700.0
  }) {
    ... on SolarPanelType {
      id
      name
      maxCapacityW
    }
  }
}
```

## Testing the Simulation

### Solar Panel Simulation
Solar panels produce power based on time of day:
- **Night (2 AM)**: 0 watts
- **Morning (8 AM)**: Moderate output
- **Noon (12 PM)**: Maximum output
- **Evening (6 PM)**: Declining output

### Electric Vehicle Schedule
EVs follow a realistic commute schedule:
- **Weekday 7 AM - 6 PM**: Offline (driving)
- **Weekday evenings & nights**: Home, charging
- **Weekends**: Always home, charging

To test: Check EV mode at different times or wait for the schedule to change.

### Battery Behavior
Batteries automatically:
- **Charge** when below 50% capacity
- **Discharge** when above 70% capacity
- **Idle** between 50-70%

## Viewing Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f web
docker compose logs -f celery
docker compose logs -f celery-beat
```

## Stopping the System

```bash
# Stop services (keeps data)
docker compose down

# Stop and remove all data
docker compose down -v
```

## Troubleshooting

### No energy statistics returned

**Problem**: GraphQL query returns zeros for all values.

**Solution**: Wait 60 seconds for the first simulation cycle to complete. Check celery-beat logs:

```bash
docker compose logs celery-beat | grep "run-energy-simulation"
```

### Permission denied errors

**Problem**: Docker permission errors during build.

**Solution**: Ensure Docker Desktop is running and you have proper permissions.

### Port already in use

**Problem**: Cannot start service, port 8000/5432/6379 already in use.

**Solution**:
```bash
# Find and stop the conflicting process
lsof -ti:8000 | xargs kill -9
# Or change the port in docker-compose.yml
```

### Simulation not updating

**Problem**: Energy stats don't change over time.

**Solution**: Check if celery-beat is running:
```bash
docker compose ps
docker compose restart celery-beat
```

## Admin Panel Usage

Access http://localhost:8000/admin with your superuser credentials.

**Useful Operations**:
- View all devices across users
- Edit device properties (status, charge levels)
- Filter by device type, status, user
- Search by device name or user

## Running Tests

```bash
# Run all tests
docker compose exec web pytest

# Run with coverage
docker compose exec web pytest --cov=apps

# Run specific test file
docker compose exec web pytest tests/test_devices/test_models.py

# Run with verbose output
docker compose exec web pytest -v
```

## Development Workflow

1. **Make code changes** - Edit files locally (they're mounted as volumes)
2. **Restart service** - `docker compose restart web`
3. **View logs** - `docker compose logs -f web`
4. **Run tests** - `docker compose exec web pytest`

## Next Steps

- Read [README.md](README.md) for full API documentation
- Read [DESIGN.md](DESIGN.md) for architecture details
- Explore the GraphQL schema in the playground
- Create your own device configurations
- Monitor energy flow in real-time

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review logs: `docker compose logs -f`
3. Verify all services are healthy: `docker compose ps`
4. Try a clean restart: `docker compose down -v && docker compose up --build`
