# Changelog

All notable changes to the Daylight Energy Management System project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- WebSocket support for real-time updates
- User notifications for device status changes
- Historical data visualization and analytics
- Mobile responsive improvements
- Advanced energy optimization algorithms
- Weather API integration for solar predictions

---

## [1.2.0] - 2024-02-10

### Added
- **React Frontend Application**
  - Modern TypeScript + React dashboard
  - TailwindCSS styling
  - JWT authentication with auto-refresh
  - Real-time energy statistics display
  - Device management interface
  - Responsive design
  - Docker containerization

### Fixed
- Django admin dark theme styling improvements
- Admin panel navigation issues resolved
- HTML rendering security hardening
- Admin device list view optimizations

### Changed
- Updated Docker Compose to include frontend service
- Enhanced documentation with frontend setup instructions
- Improved authentication flow across all interfaces

---

## [1.1.0] - 2024-02-09

### Added
- **Django Dashboard Views**
  - Server-rendered dashboard with energy statistics
  - Device management interface
  - Real-time data visualization
  - Interactive charts and graphs
  - Demo mode for testing

### Improved
- **Enhanced Django Admin**
  - Custom dark theme implementation
  - Bulk actions (activate, deactivate, delete devices)
  - Advanced filtering by device type, status, user
  - Search functionality
  - Custom admin site configuration
  - Improved device list display

### Fixed
- Admin panel styling inconsistencies
- Navigation menu issues
- Permission checks for device management

---

## [1.0.0] - 2024-02-09

### Added
- **Core Energy Management System**
  - Multi-table inheritance device model architecture
  - Six device types (Solar, Generator, Battery, EV, AC, Heater)
  - User-device relationship management
  - Device status tracking (online, offline, error)

- **GraphQL API (Strawberry)**
  - Complete schema with queries and mutations
  - Device queries (allDevices)
  - Energy statistics query
  - Device creation and updates
  - JWT authentication integration
  - GraphQL Playground interface

- **REST API (Django REST Framework)**
  - Full CRUD operations for all device types
  - JWT token authentication endpoints
  - User management endpoints
  - Device statistics endpoint
  - ViewSets for each device type
  - Serializers for data validation
  - Permission classes for authorization

- **Real-Time Simulation System**
  - Celery worker and beat configuration
  - 60-second simulation cycle
  - Device-specific simulators:
    - Solar panel: Solar elevation angle calculations
    - Generator: Steady output with variation
    - Battery: Intelligent charge/discharge logic
    - EV: Schedule-based availability (weekday commute)
    - Consumption devices: Variable power draw
  - Redis caching for real-time data (60s TTL)
  - Aggregated user-level energy statistics

- **Database & Infrastructure**
  - PostgreSQL database setup
  - Redis for caching and Celery broker
  - Docker Compose orchestration
  - Health check endpoint
  - Environment variable configuration

- **Testing Infrastructure**
  - Pytest configuration
  - Factory Boy for test fixtures
  - Device model tests
  - API authentication tests
  - Test coverage reporting

- **Documentation**
  - Comprehensive README
  - Quick Start Guide
  - Design documentation
  - Docker setup instructions
  - API usage examples

### Technical Details

#### Device Models
- Base `Device` model with polymorphic behavior
- Production devices: `SolarPanel`, `Generator`
- Storage devices: `Battery`, `ElectricVehicle`
- Consumption devices: `AirConditioner`, `Heater`
- Shared fields: name, status, user, timestamps
- Device-specific fields for configuration

#### Simulation Logic
- **Solar Panels**: Time and location-based generation
  - Solar elevation angle calculation
  - Clear-sky irradiance model
  - Cloud cover simulation (85-100%)
  - Zero output at night
  
- **Electric Vehicles**: Realistic commute patterns
  - Weekday 7 AM - 6 PM: Offline (driving)
  - Weekday evenings/nights: Home, charging
  - Weekends: Always home
  - Configurable driving efficiency (default: 3 kWh/hour)
  - Charge target: 90% capacity
  
- **Batteries**: Smart charge/discharge
  - Charge when below 50%
  - Discharge when above 70%
  - Idle between 50-70%
  - Respects C-rate limits

#### Redis Key Schema
```
device:{device_id}:current       # Current power (W)
device:{device_id}:storage       # Storage state (kWh, %)
device:{device_id}:last_seen     # EV last seen timestamp
user:{user_id}:energy_stats      # Aggregated statistics
```

#### API Features
- JWT token authentication with refresh
- User filtering (non-admin see only their devices)
- Admin users see all devices
- GraphQL union types for polymorphic devices
- REST API pagination support
- Comprehensive error handling

---

## [0.3.0] - 2024-02-08

### Added
- REST API implementation
- JWT authentication for REST endpoints
- Device ViewSets for all device types
- User management endpoints
- API serializers and validators
- Token refresh and verification endpoints

### Changed
- Separated API into GraphQL and REST modules
- Updated URL routing for dual API support
- Enhanced permission system

---

## [0.2.0] - 2024-02-07

### Added
- GraphQL API implementation with Strawberry
- Complete GraphQL schema
- Device queries and mutations
- Energy statistics query
- GraphQL Playground integration

### Changed
- Restructured API module for GraphQL
- Updated authentication to support GraphQL

---

## [0.1.0] - 2024-02-06

### Added
- Initial project setup
- Django 5.1 configuration
- PostgreSQL database integration
- Redis integration
- Device models implementation
- Basic Celery configuration
- Docker setup
- Initial documentation

### Infrastructure
- Project structure with apps (devices, api, simulation)
- Split settings (base, development, production)
- Environment variable configuration
- Docker Compose orchestration
- Makefile for common commands

---

## Development History

### Design Decisions

#### Multi-Table Inheritance
Chosen over Single-Table or Abstract Base Classes for:
- Clean separation of device-specific fields
- Easy querying of specific device types
- Django admin integration
- Type-safe GraphQL schema

#### Celery + Redis Simulation
- Decoupled simulation from API layer
- Scalable task processing
- Real-time data without API polling
- 60-second TTL prevents stale data

#### Dual API (GraphQL + REST)
- GraphQL for flexible client queries (frontend)
- REST for standard CRUD operations (integrations)
- Same authentication and business logic
- Allows clients to choose their preference

#### Docker Compose
- Consistent development environment
- Easy service orchestration
- Production-like setup locally
- Simple onboarding for developers

### Known Issues

#### Fixed in 1.2.0
- ✅ Admin panel dark theme inconsistencies
- ✅ Navigation menu styling
- ✅ HTML rendering security concerns

#### Fixed in 1.1.0
- ✅ Admin panel not accessible
- ✅ Device filtering issues
- ✅ Permission checks missing

#### Fixed in 1.0.0
- ✅ Simulation not running consistently
- ✅ Redis connection issues
- ✅ Device type detection errors
- ✅ EV schedule logic bugs

### Migration Guide

#### From 0.x to 1.0
No breaking changes. Run migrations:
```bash
docker compose exec web python manage.py migrate
```

#### From 1.0 to 1.1
No breaking changes. Update Docker Compose and restart:
```bash
docker compose down
docker compose up --build
```

#### From 1.1 to 1.2
Frontend added. Update Docker Compose and rebuild:
```bash
docker compose down
docker compose up --build
```

Access frontend at http://localhost:3000

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines and how to contribute to this project.

## Release Process

1. Update version in relevant files
2. Update CHANGELOG.md with changes
3. Create git tag: `git tag -a v1.2.0 -m "Release 1.2.0"`
4. Push changes: `git push && git push --tags`
5. Build and test Docker images
6. Deploy to production environment

---

## Links

- [GitHub Repository](https://github.com/your-username/Daylight)
- [Documentation](README.md)
- [API Documentation](API_DOCS.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Issue Tracker](https://github.com/your-username/Daylight/issues)
