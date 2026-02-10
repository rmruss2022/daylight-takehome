# API Documentation

Complete reference for the Daylight Energy Management System APIs.

## Table of Contents

- [Authentication](#authentication)
- [REST API](#rest-api)
- [GraphQL API](#graphql-api)
- [Response Formats](#response-formats)
- [Error Handling](#error-handling)

## Authentication

Both APIs use JWT (JSON Web Token) authentication.

### Obtaining a Token

#### REST API
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### GraphQL API
```graphql
mutation {
  loginUser(username: "your_username", password: "your_password") {
    token
    user {
      id
      username
      email
    }
  }
}
```

**Response:**
```json
{
  "data": {
    "loginUser": {
      "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "user": {
        "id": 1,
        "username": "your_username",
        "email": "user@example.com"
      }
    }
  }
}
```

### Using the Token

#### REST API
Include in the `Authorization` header:
```bash
curl http://localhost:8000/api/devices/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### GraphQL API
In the HTTP Headers section of the GraphQL Playground:
```json
{
  "Authorization": "Bearer YOUR_TOKEN"
}
```

### Refreshing Tokens

#### REST API
```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

#### Token Verification
```bash
curl -X POST http://localhost:8000/api/auth/token/verify/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "YOUR_ACCESS_TOKEN"
  }'
```

---

## REST API

Base URL: `http://localhost:8000/api`

### Endpoints Overview

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/auth/token/` | POST | Obtain JWT token |
| `/auth/token/refresh/` | POST | Refresh JWT token |
| `/users/` | GET, POST | User management (admin only) |
| `/users/me/` | GET | Current user info |
| `/devices/` | GET, POST, PUT, PATCH, DELETE | All devices |
| `/devices/stats/` | GET | Device statistics |
| `/batteries/` | GET, POST, PUT, PATCH, DELETE | Battery devices |
| `/electric-vehicles/` | GET, POST, PUT, PATCH, DELETE | EV devices |
| `/solar-panels/` | GET, POST, PUT, PATCH, DELETE | Solar panel devices |
| `/generators/` | GET, POST, PUT, PATCH, DELETE | Generator devices |
| `/air-conditioners/` | GET, POST, PUT, PATCH, DELETE | AC devices |
| `/heaters/` | GET, POST, PUT, PATCH, DELETE | Heater devices |

### Authentication Endpoints

#### POST `/api/auth/token/`
Obtain access and refresh tokens.

**Request Body:**
```json
{
  "username": "testuser1",
  "password": "testpass123"
}
```

**Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### POST `/api/auth/token/refresh/`
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### User Endpoints

#### GET `/api/users/me/`
Get current authenticated user information.

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Response (200):**
```json
{
  "id": 1,
  "username": "testuser1",
  "email": "test@example.com",
  "first_name": "Test",
  "last_name": "User"
}
```

### Device Endpoints

#### GET `/api/devices/`
List all devices for the authenticated user.

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Query Parameters:**
- `page` (optional): Page number for pagination
- `page_size` (optional): Number of results per page

**Response (200):**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Rooftop Solar",
      "status": "online",
      "device_type": "solar_panel",
      "created_at": "2024-02-10T12:00:00Z",
      "updated_at": "2024-02-10T12:30:00Z"
    },
    {
      "id": 2,
      "name": "Home Battery",
      "status": "online",
      "device_type": "battery",
      "created_at": "2024-02-10T12:00:00Z",
      "updated_at": "2024-02-10T12:30:00Z"
    }
  ]
}
```

#### GET `/api/devices/{id}/`
Retrieve a specific device.

**Response (200):**
```json
{
  "id": 1,
  "name": "Rooftop Solar",
  "status": "online",
  "device_type": "solar_panel",
  "created_at": "2024-02-10T12:00:00Z",
  "updated_at": "2024-02-10T12:30:00Z"
}
```

#### GET `/api/devices/stats/`
Get device statistics for the authenticated user.

**Response (200):**
```json
{
  "total": 10,
  "online": 8,
  "offline": 1,
  "error": 1
}
```

#### POST `/api/batteries/`
Create a new battery device.

**Request Body:**
```json
{
  "name": "Tesla Powerwall",
  "capacity_kwh": 13.5,
  "current_charge_kwh": 6.75,
  "max_charge_rate_kw": 5.0,
  "max_discharge_rate_kw": 5.0
}
```

**Response (201):**
```json
{
  "id": 3,
  "name": "Tesla Powerwall",
  "status": "online",
  "capacity_kwh": 13.5,
  "current_charge_kwh": 6.75,
  "max_charge_rate_kw": 5.0,
  "max_discharge_rate_kw": 5.0,
  "charge_percentage": 50.0,
  "created_at": "2024-02-10T13:00:00Z",
  "updated_at": "2024-02-10T13:00:00Z"
}
```

#### POST `/api/solar-panels/`
Create a new solar panel device.

**Request Body:**
```json
{
  "name": "Rooftop Solar Array",
  "panel_area_m2": 20.0,
  "efficiency": 0.20,
  "max_capacity_w": 4000.0,
  "latitude": 37.77,
  "longitude": -122.42
}
```

**Response (201):**
```json
{
  "id": 4,
  "name": "Rooftop Solar Array",
  "status": "online",
  "panel_area_m2": 20.0,
  "efficiency": 0.20,
  "max_capacity_w": 4000.0,
  "latitude": 37.77,
  "longitude": -122.42,
  "created_at": "2024-02-10T13:00:00Z",
  "updated_at": "2024-02-10T13:00:00Z"
}
```

#### POST `/api/electric-vehicles/`
Create a new EV device.

**Request Body:**
```json
{
  "name": "Tesla Model 3",
  "capacity_kwh": 75.0,
  "current_charge_kwh": 60.0,
  "max_charge_rate_kw": 11.0,
  "max_discharge_rate_kw": 11.0,
  "mode": "charging",
  "driving_efficiency_kwh_per_hour": 3.0
}
```

**Response (201):**
```json
{
  "id": 5,
  "name": "Tesla Model 3",
  "status": "online",
  "capacity_kwh": 75.0,
  "current_charge_kwh": 60.0,
  "max_charge_rate_kw": 11.0,
  "max_discharge_rate_kw": 11.0,
  "mode": "charging",
  "charge_percentage": 80.0,
  "driving_efficiency_kwh_per_hour": 3.0,
  "last_seen_at": "2024-02-10T13:00:00Z",
  "created_at": "2024-02-10T13:00:00Z",
  "updated_at": "2024-02-10T13:00:00Z"
}
```

#### PUT/PATCH `/api/devices/{id}/`
Update a device.

**Request Body (PATCH):**
```json
{
  "name": "Updated Name",
  "status": "offline"
}
```

**Response (200):**
```json
{
  "id": 1,
  "name": "Updated Name",
  "status": "offline",
  "device_type": "solar_panel",
  "created_at": "2024-02-10T12:00:00Z",
  "updated_at": "2024-02-10T13:30:00Z"
}
```

#### DELETE `/api/devices/{id}/`
Delete a device.

**Response (204):** No content

---

## GraphQL API

Endpoint: `http://localhost:8000/graphql`

### Schema Overview

#### Types

**DeviceUnion**
```graphql
union DeviceUnion = 
  | SolarPanelType
  | GeneratorType
  | BatteryType
  | ElectricVehicleType
  | AirConditionerType
  | HeaterType
```

**EnergyStatsType**
```graphql
type EnergyStatsType {
  currentProduction: Float!
  currentConsumption: Float!
  currentStorage: StorageStatsType!
  currentStorageFlow: Float!
  netGridFlow: Float!
}
```

**StorageStatsType**
```graphql
type StorageStatsType {
  totalCapacityWh: Float!
  currentLevelWh: Float!
  percentage: Float!
}
```

### Queries

#### `allDevices`
Get all devices for the authenticated user.

**Query:**
```graphql
query {
  allDevices {
    ... on SolarPanelType {
      id
      name
      status
      panelAreaM2
      efficiency
      maxCapacityW
      latitude
      longitude
      createdAt
      updatedAt
    }
    ... on BatteryType {
      id
      name
      status
      capacityKwh
      currentChargeKwh
      maxChargeRateKw
      maxDischargeRateKw
      chargePercentage
      createdAt
      updatedAt
    }
    ... on ElectricVehicleType {
      id
      name
      status
      capacityKwh
      currentChargeKwh
      maxChargeRateKw
      maxDischargeRateKw
      mode
      chargePercentage
      drivingEfficiencyKwhPerHour
      lastSeenAt
      createdAt
      updatedAt
    }
    ... on GeneratorType {
      id
      name
      status
      ratedOutputW
      createdAt
      updatedAt
    }
    ... on AirConditionerType {
      id
      name
      status
      ratedPowerW
      minPowerW
      maxPowerW
      createdAt
      updatedAt
    }
    ... on HeaterType {
      id
      name
      status
      ratedPowerW
      minPowerW
      maxPowerW
      createdAt
      updatedAt
    }
  }
}
```

**Response:**
```json
{
  "data": {
    "allDevices": [
      {
        "id": 1,
        "name": "Rooftop Solar",
        "status": "ONLINE",
        "panelAreaM2": 20.0,
        "efficiency": 0.2,
        "maxCapacityW": 4000.0,
        "latitude": 37.77,
        "longitude": -122.42,
        "createdAt": "2024-02-10T12:00:00",
        "updatedAt": "2024-02-10T12:30:00"
      }
    ]
  }
}
```

#### `energyStats`
Get real-time energy statistics for the authenticated user.

**Query:**
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

**Response:**
```json
{
  "data": {
    "energyStats": {
      "currentProduction": 2500.0,
      "currentConsumption": 1800.0,
      "currentStorage": {
        "totalCapacityWh": 88500.0,
        "currentLevelWh": 44250.0,
        "percentage": 50.0
      },
      "currentStorageFlow": 700.0,
      "netGridFlow": 0.0
    }
  }
}
```

**Field Descriptions:**
- `currentProduction`: Total watts being generated (solar + generators)
- `currentConsumption`: Total watts being consumed (AC + heaters)
- `currentStorageFlow`: Positive = charging, Negative = discharging
- `netGridFlow`: Positive = importing from grid, Negative = exporting to grid

### Mutations

#### `loginUser`
Authenticate and receive JWT token.

**Mutation:**
```graphql
mutation {
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

**Response:**
```json
{
  "data": {
    "loginUser": {
      "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "user": {
        "id": 1,
        "username": "testuser1",
        "email": "test@example.com"
      }
    }
  }
}
```

#### `createDevice`
Create a new device.

**Mutation (Solar Panel):**
```graphql
mutation {
  createDevice(input: {
    name: "New Solar Panel"
    deviceType: SOLAR_PANEL
    panelAreaM2: 15.0
    efficiency: 0.18
    maxCapacityW: 2700.0
    latitude: 37.77
    longitude: -122.42
  }) {
    ... on SolarPanelType {
      id
      name
      maxCapacityW
      status
    }
  }
}
```

**Mutation (Battery):**
```graphql
mutation {
  createDevice(input: {
    name: "Home Battery"
    deviceType: BATTERY
    capacityKwh: 13.5
    currentChargeKwh: 6.75
    maxChargeRateKw: 5.0
    maxDischargeRateKw: 5.0
  }) {
    ... on BatteryType {
      id
      name
      capacityKwh
      chargePercentage
    }
  }
}
```

**Mutation (Electric Vehicle):**
```graphql
mutation {
  createDevice(input: {
    name: "Tesla Model 3"
    deviceType: ELECTRIC_VEHICLE
    capacityKwh: 75.0
    currentChargeKwh: 60.0
    maxChargeRateKw: 11.0
    maxDischargeRateKw: 11.0
    mode: CHARGING
    drivingEfficiencyKwhPerHour: 3.0
  }) {
    ... on ElectricVehicleType {
      id
      name
      mode
      chargePercentage
    }
  }
}
```

**Mutation (Generator):**
```graphql
mutation {
  createDevice(input: {
    name: "Backup Generator"
    deviceType: GENERATOR
    ratedOutputW: 5000.0
  }) {
    ... on GeneratorType {
      id
      name
      ratedOutputW
    }
  }
}
```

**Mutation (Air Conditioner):**
```graphql
mutation {
  createDevice(input: {
    name: "Living Room AC"
    deviceType: AIR_CONDITIONER
    minPowerW: 800.0
    maxPowerW: 2000.0
  }) {
    ... on AirConditionerType {
      id
      name
      minPowerW
      maxPowerW
    }
  }
}
```

**Mutation (Heater):**
```graphql
mutation {
  createDevice(input: {
    name: "Bedroom Heater"
    deviceType: HEATER
    minPowerW: 500.0
    maxPowerW: 1500.0
  }) {
    ... on HeaterType {
      id
      name
      minPowerW
      maxPowerW
    }
  }
}
```

#### `updateDevice`
Update an existing device.

**Mutation:**
```graphql
mutation {
  updateDevice(id: 1, input: {
    name: "Updated Device Name"
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

**Update Battery Charge:**
```graphql
mutation {
  updateDevice(id: 2, input: {
    currentChargeKwh: 10.0
  }) {
    ... on BatteryType {
      id
      currentChargeKwh
      chargePercentage
    }
  }
}
```

**Update EV Mode:**
```graphql
mutation {
  updateDevice(id: 3, input: {
    mode: DISCHARGING
  }) {
    ... on ElectricVehicleType {
      id
      mode
    }
  }
}
```

### Enums

#### DeviceTypeEnum
```graphql
enum DeviceTypeEnum {
  SOLAR_PANEL
  GENERATOR
  BATTERY
  ELECTRIC_VEHICLE
  AIR_CONDITIONER
  HEATER
}
```

#### DeviceStatusEnum
```graphql
enum DeviceStatusEnum {
  ONLINE
  OFFLINE
  ERROR
}
```

#### EVModeEnum
```graphql
enum EVModeEnum {
  CHARGING
  DISCHARGING
  OFFLINE
}
```

---

## Response Formats

### Success Response (REST)
```json
{
  "id": 1,
  "name": "Device Name",
  "status": "online",
  "created_at": "2024-02-10T12:00:00Z"
}
```

### Success Response (GraphQL)
```json
{
  "data": {
    "fieldName": "value"
  }
}
```

### Pagination (REST)
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/devices/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## Error Handling

### REST API Errors

#### 400 Bad Request
```json
{
  "field_name": [
    "This field is required."
  ]
}
```

#### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

#### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### GraphQL API Errors

```json
{
  "data": null,
  "errors": [
    {
      "message": "Device not found or you don't have permission to update it",
      "locations": [
        {
          "line": 2,
          "column": 3
        }
      ],
      "path": [
        "updateDevice"
      ]
    }
  ]
}
```

### Common Error Scenarios

| Scenario | REST Status | GraphQL Response | Solution |
|----------|-------------|------------------|----------|
| Missing token | 401 | Error in response | Provide Authorization header |
| Invalid token | 401 | Error in response | Refresh or re-authenticate |
| Permission denied | 403 | Error in response | Check user permissions |
| Resource not found | 404 | Error in response | Verify resource ID |
| Validation error | 400 | Error in response | Check request body format |
| Server error | 500 | Error in response | Check server logs |

---

## Rate Limiting

Currently, no rate limiting is implemented. For production deployments, consider implementing rate limiting at the API gateway or application level.

## Webhooks

Webhooks are not currently supported but can be added for real-time event notifications.

## Versioning

The API is currently unversioned. Future versions may introduce versioning through:
- URL path: `/api/v2/devices/`
- HTTP header: `Accept: application/vnd.daylight.v2+json`

## Support

For API issues or questions:
1. Check this documentation
2. Review error messages and logs
3. Consult the main [README.md](README.md)
4. Examine test files in `/tests` for usage examples
