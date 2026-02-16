# Daylight Energy Management System

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/django-5.1-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/react-19.2-blue.svg)](https://reactjs.org/)
[![GraphQL](https://img.shields.io/badge/graphql-strawberry-ff69b4.svg)](https://strawberry.rocks/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A comprehensive smart home energy management system with real-time monitoring, device simulation, and dual API support (GraphQL + REST). Built with Django, React, and Docker for production-ready deployment.


## 🚀 Quick Start

### Prerequisites

- **Docker Desktop** (with Docker Compose)
- **Git**
- **Node.js 18+** (for local frontend development)
- At least **4GB RAM** available

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Daylight
   ```

2. **Copy environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration (optional for development)
   ```

3. **Start all services**
   ```bash
   docker compose up --build
   ```

   This starts:
   - `web`: Django application (port 8000)
   - `frontend`: React application (port 3000)
   - `db`: PostgreSQL database (port 5432)
   - `redis`: Redis cache (port 6379)
   - `celery`: Background worker
   - `celery-beat`: Task scheduler

4. **Initialize database** (in a new terminal)
   ```bash
   # Run migrations
   docker compose exec web python manage.py migrate

   # Create admin user
   docker compose exec web python manage.py createsuperuser

   # (Optional) Load sample data
   docker compose exec web python manage.py seed_devices
   ```

## 🌟 Features

### Core Capabilities
- **Multi-Device Support**: Solar panels, batteries, EVs, generators, air conditioners, and heaters
- **Real-Time Monitoring**: Live energy production, consumption, storage, and grid flow statistics
- **Realistic Simulation**: Celery-powered background tasks with time-based behavior patterns
- **Dual API Architecture**: GraphQL (Strawberry) and REST API (Django REST Framework)
- **Modern Frontend**: React + TypeScript + TailwindCSS dashboard
- **JWT Authentication**: Secure token-based authentication for both APIs
- **Admin Interface**: Enhanced Django admin with custom actions and dark theme

### Device Types

#### Production Devices
- **Solar Panels**: Solar elevation angle calculations, location-based generation
- **Generators**: Steady power output with realistic variation

#### Storage Devices
- **Batteries**: Intelligent charge/discharge logic with C-rate limiting
- **Electric Vehicles**: Schedule-based availability (commute simulation), V2H support

#### Consumption Devices
- **Air Conditioners**: Variable power consumption
- **Heaters**: Adjustable power draw

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  ┌──────────────────┐  ┌─────────────────┐  ┌─────────────────┐│
│  │  React Frontend  │  │  GraphQL Client │  │   REST Client   ││
│  │  (Port 3000)     │  │  (Playground)   │  │   (API Tools)   ││
│  └──────────────────┘  └─────────────────┘  └─────────────────┘│
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────┼─────────────────────────────────┐
│                         API Layer                                │
│  ┌──────────────────┐  ┌─────────────────┐  ┌─────────────────┐│
│  │   Django Views   │  │  GraphQL Schema │  │  REST ViewSets  ││
│  │   (Dashboard)    │  │   (Strawberry)  │  │      (DRF)      ││
│  └──────────────────┘  └─────────────────┘  └─────────────────┘│
│                                │                                 │
│  ┌────────────────────────────┴──────────────────────────────┐ │
│  │               JWT Authentication & Permissions              │ │
│  └────────────────────────────┬──────────────────────────────┘ │
└───────────────────────────────┼─────────────────────────────────┘
                                │
┌───────────────────────────────┼─────────────────────────────────┐
│                      Business Logic Layer                        │
│  ┌────────────────────────────┴──────────────────────────────┐ │
│  │                      Django Models                          │ │
│  │  Device (Base) → SolarPanel, Battery, EV, Generator, etc.  │ │
│  └────────────────────────────┬──────────────────────────────┘ │
└───────────────────────────────┼─────────────────────────────────┘
                                │
┌───────────────────────────────┼─────────────────────────────────┐
│                     Simulation & Cache Layer                     │
│  ┌─────────────────┐  ┌──────┴──────┐  ┌────────────────────┐ │
│  │  Celery Beat    │→ │   Celery    │→ │  Redis Cache       │ │
│  │  (Scheduler)    │  │   Worker    │  │  (Real-time Data)  │ │
│  │  60s interval   │  │  Simulators │  │  60s TTL           │ │
│  └─────────────────┘  └─────────────┘  └────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
┌───────────────────────────────┼─────────────────────────────────┐
│                        Data Layer                                │
│  ┌────────────────────────────┴──────────────────────────────┐ │
│  │                    PostgreSQL Database                      │ │
│  │         (Persistent device configuration & state)          │ │
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Celery Beat** triggers simulation every 60 seconds
2. **Orchestrator** spawns parallel tasks for each device
3. **Device Simulators** calculate realistic energy values
4. **Redis** stores current state with 60-second TTL
5. **API Layer** aggregates and serves data to clients

## ☁️ Deploy to Production

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/rmruss2022/daylight-takehome)

**One-click deployment to Railway** - Automatically sets up Django, PostgreSQL, Redis, and Celery workers.

For detailed deployment instructions, see **[DEPLOYMENT.md](DEPLOYMENT.md)**.


### Access Points

| Service | URL | Description |
|---------|-----|-------------|
| React Frontend | http://localhost:3000 | Modern dashboard UI |
| Django Dashboard | http://localhost:8000 | Server-rendered dashboard |
| Django Admin | http://localhost:8000/admin | Admin interface |
| GraphQL Playground | http://localhost:8000/graphql | Interactive GraphQL API |
| REST API | http://localhost:8000/api | RESTful endpoints |
| Health Check | http://localhost:8000/health | Service health status |

## 📖 Usage Guide

### React Frontend (Recommended)

1. Navigate to http://localhost:3000
2. Login with your credentials
3. View real-time energy statistics
4. Monitor device status and performance
5. View energy production, consumption, and storage

### GraphQL API

1. **Get JWT Token**
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

2. **Set Authorization Header**
   ```json
   {
     "Authorization": "Bearer YOUR_TOKEN_HERE"
   }
   ```

3. **Query Energy Stats**
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

### REST API

1. **Obtain Token**
   ```bash
   curl -X POST http://localhost:8000/api/auth/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser1", "password": "testpass123"}'
   ```

2. **List Devices**
   ```bash
   curl http://localhost:8000/api/devices/ \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
   ```

See [API_DOCS.md](API_DOCS.md) for complete API documentation.

### Django Admin

1. Navigate to http://localhost:8000/admin
2. Login with superuser credentials
3. Manage devices, users, and configurations
4. Use bulk actions (activate, deactivate, delete)
5. Filter by device type, status, and user

## 🧪 Testing

### Django Backend Tests

#### Run All Tests
```bash
docker compose exec web pytest
```

#### Run with Coverage
```bash
docker compose exec web pytest --cov=apps --cov-report=html
```

#### Run Specific Test File
```bash
docker compose exec web pytest tests/test_devices/test_models.py
```

#### Run with Verbose Output
```bash
docker compose exec web pytest -v
```

### End-to-End Tests

The project includes Playwright E2E tests that verify both the Django and React frontends.

#### Prerequisites
```bash
# Install Playwright (from project root)
npm install
npx playwright install chromium
```

#### Run E2E Tests
```bash
# Make sure Django (port 8000) and React (port 3000) are running
docker compose up -d

# Run all E2E tests
npm run test:e2e

# Run with UI mode (interactive)
npm run test:e2e:ui

# Run in debug mode
npm run test:e2e:debug
```

#### Test Coverage
- **Django Dashboard**: Login, energy overview, device management, navigation
- **React Frontend**: JWT authentication, dashboard stats, battery management, protected routes

## 🛠️ Development

### Project Structure
```
Daylight/
├── apps/
│   ├── api/              # GraphQL & REST API
│   │   ├── mutations/    # GraphQL mutations
│   │   ├── queries/      # GraphQL queries
│   │   ├── types/        # GraphQL types
│   │   ├── rest_views.py # REST viewsets
│   │   └── serializers.py
│   ├── devices/          # Device models & admin
│   │   ├── models/       # Device models
│   │   ├── admin.py      # Admin configuration
│   │   └── views.py      # Dashboard views
│   └── simulation/       # Celery tasks
│       ├── simulators/   # Device simulators
│       └── tasks.py      # Celery tasks
├── config/               # Django configuration
│   ├── settings/         # Split settings
│   ├── urls.py          # URL routing
│   └── celery.py        # Celery configuration
├── frontend/             # React application
│   └── src/
│       ├── components/   # React components
│       ├── pages/        # Page components
│       ├── api/          # API client
│       └── context/      # React context
├── tests/                # Test suite
├── docker-compose.yml    # Service orchestration
└── Dockerfile           # Container definition
```

### Environment Variables

Key variables (see `.env.example` for complete list):

```bash
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database
POSTGRES_DB=smart_home_energy
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
JWT_EXPIRY_HOURS=24
```

### Local Development Workflow

1. **Make code changes** (files are mounted as volumes)
2. **Restart service**
   ```bash
   docker compose restart web
   ```
3. **View logs**
   ```bash
   docker compose logs -f web
   ```
4. **Run tests**
   ```bash
   docker compose exec web pytest
   ```

### Database Management

**Reset Database**
```bash
docker compose down -v
docker compose up -d db
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

**Django Shell**
```bash
docker compose exec web python manage.py shell
```

**PostgreSQL Access**
```bash
docker compose exec db psql -U postgres -d smart_home_energy
```

### Redis Debugging

**Redis CLI**
```bash
docker compose exec redis redis-cli
```

**View Keys**
```bash
docker compose exec redis redis-cli KEYS "user:*"
```

**Get Energy Stats**
```bash
docker compose exec redis redis-cli GET "user:1:energy_stats"
```

## 🔧 Simulation Details

### Solar Panel Simulation
- Uses solar elevation angle based on time and location
- Clear-sky irradiance model
- Random cloud cover (85-100%)
- Zero output at night
- Default location: San Francisco (37.77°N, 122.42°W)

### Electric Vehicle Schedule
- **Weekdays 7 AM - 6 PM**: Offline (driving)
- **Weekday evenings/nights**: Home, charging
- **Weekends**: Always home
- Driving consumption: 3 kWh/hour (configurable)
- Charge target: 90% capacity

### Battery Logic
- **Charge**: When below 50% capacity
- **Discharge**: When above 70% capacity
- **Idle**: Between 50-70%
- Respects C-rate limits (charge/discharge rates)

### Redis Key Schema
```
device:{device_id}:current       # Current power (W)
device:{device_id}:storage       # Storage state (kWh, %)
device:{device_id}:last_seen     # EV last seen timestamp
user:{user_id}:energy_stats      # Aggregated stats
```

## 🚢 Deployment

### Production Considerations

1. **Environment Variables**
   - Set `DEBUG=False`
   - Use strong `SECRET_KEY` and `JWT_SECRET_KEY`
   - Configure `ALLOWED_HOSTS`

2. **Database**
   - Use managed PostgreSQL (AWS RDS, Google Cloud SQL)
   - Enable backups and replication

3. **Redis**
   - Use managed Redis (AWS ElastiCache, Redis Cloud)
   - Configure persistence if needed

4. **Static Files**
   ```bash
   python manage.py collectstatic --no-input
   ```
   - Serve with Nginx or CDN

5. **WSGI Server**
   - Replace `runserver` with Gunicorn or uWSGI
   - Example: `gunicorn config.wsgi:application --bind 0.0.0.0:8000`

6. **Monitoring**
   - Use health check endpoint: `/health`
   - Monitor Celery worker/beat status
   - Track Redis memory usage

## 📚 Additional Documentation

- [API Documentation](API_DOCS.md) - Complete API reference
- [Changelog](CHANGELOG.md) - Version history and changes
- [Contributing Guide](CONTRIBUTING.md) - Development guidelines
- [Quick Start Guide](QUICKSTART.md) - Simplified setup instructions

## 🐛 Troubleshooting

### No Energy Statistics

**Problem**: GraphQL/API returns zeros for all values.

**Solution**: Wait 60 seconds for first simulation cycle. Check logs:
```bash
docker compose logs celery-beat | grep "run-energy-simulation"
```

### Simulation Not Running

**Problem**: Values don't update over time.

**Solution**: Verify Celery Beat is running:
```bash
docker compose ps
docker compose restart celery-beat
```

### Permission Errors

**Problem**: "Authentication credentials not provided"

**Solution**: Ensure JWT token is in Authorization header:
```
Authorization: Bearer YOUR_TOKEN_HERE
```

### Port Already in Use

**Problem**: Cannot start service, port conflict.

**Solution**: Stop conflicting process or change port in `docker-compose.yml`.

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## 📝 License

This project is a technical assessment implementation for Daylight.

## 🙏 Acknowledgments

Built with:
- [Django](https://www.djangoproject.com/) - Web framework
- [Strawberry GraphQL](https://strawberry.rocks/) - GraphQL library
- [Django REST Framework](https://www.django-rest-framework.org/) - REST API
- [React](https://reactjs.org/) - Frontend framework
- [Celery](https://docs.celeryproject.org/) - Task queue
- [PostgreSQL](https://www.postgresql.org/) - Database
- [Redis](https://redis.io/) - Cache and message broker
