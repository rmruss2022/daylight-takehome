Backend Engineer Technical Assessment
Overview
You are tasked with developing a Dockerized Django GraphQL API backend for a Smart Home Energy Management System. The backend must handle smart devices across production, storage, and consumption categories — including user authentication, device modeling, energy simulation, and management through Django Admin.
You will have up to 8 hours to complete the take-home portion.
Submission
Submit as a GitHub repo shared with 5h44n. Include a short design document (see Deliverables).

Functional Requirements
Models
Design a data model to represent the following device types:
Production Devices: Solar Panel, Generator
Storage Devices: Battery, Electric Vehicle (EV)
Consumption Devices: Air Conditioner, Heater, Electric Vehicle (EV)
⚠️ Note on Electric Vehicles: EVs are dual-role devices. A connected EV that is charging should count as a consumption device. A connected EV that is discharging to the home should count as a storage outflow device. A disconnected EV (e.g., driving or away) should be marked offline, but its last known stored energy level must still be tracked and reflected accurately when it reconnects. Your data model and energy calculations must handle these state transitions correctly.
Each device should store common attributes including:
id
name
device_type (production, storage, consumption)
status (online, offline)
created_at, updated_at
A foreign key to the owning User
Beyond these, each device type will need attributes specific to its role. We are intentionally not prescribing the exact schema — choose a modeling approach (e.g., single-table inheritance, multi-table, polymorphic, etc.) and be prepared to explain your reasoning.
GraphQL API
Build a GraphQL API with the following capabilities:
JWT Authentication: A loginUser mutation that returns a JWT token.
Create Device: A createDevice mutation to register a new device for the authenticated user.
Retrieve Devices: An allDevices query to fetch all devices for the authenticated user.
Update Device: An updateDevice mutation to modify device attributes (name, status, etc.).
Energy Stats: An energyStats query returning computed energy statistics for the authenticated user:
Metric
Description
Current Production
Total instantaneous energy production (W) from all online production devices
Current Consumption
Total instantaneous energy consumption (W) from all online consumption devices, including EVs that are actively charging
Current Storage Level
Total capacity (Wh), current level (Wh), and percentage of max capacity across all storage devices — including offline EVs at their last known level
Current Storage Flow
Net rate (W) at which storage devices are charging (+) or discharging (−)
Net Grid Flow
current_consumption − current_production − current_storage_flow

Example response shape (you may structure this differently if you prefer):
{
  "current_production": 3500,
  "current_consumption": 4500,
  "current_storage": {
    "total_capacity_wh": 32000,
    "current_level_wh": 12000,
    "percentage": 37.5
  },
  "current_storage_flow": -500,
  "net_grid_flow": 500
}
Django Admin
Configure Django Admin to manage Users and Devices. Use your judgment on which fields to expose, which should be read-only, and what filtering/search options are useful.

Technical Requirements
Django 5.x (latest stable)
PostgreSQL
Redis (for caching simulated data)
Celery (for background simulation tasks)
Docker and Docker Compose
You are free to choose your GraphQL library, authentication approach, and any other supporting packages.

Simulating Usage Data
Since real device APIs are not available, implement a Celery periodic task that generates realistic energy data for each device at regular intervals (e.g., every 60 seconds).
Requirements
Your simulation must respect these physical constraints:
Solar panels produce energy based on time of day. Output should follow a realistic daylight curve — near zero at night, ramping up in the morning, peaking midday, and tapering off in the evening. Choose a model that feels physically plausible and document your approach and assumptions (location, season, clear-sky vs. cloud cover, etc.).
Generators produce a steady output when online (vary slightly ±5% to simulate real behavior).
Batteries cannot discharge below 0% or charge above 100% of their rated capacity. Charge/discharge rates should respect realistic C-rate limits.
EVs follow a connection schedule: assume EVs are typically away 7 AM – 6 PM on weekdays and connected otherwise. When an EV reconnects, it should resume from its last known charge level (minus estimated driving consumption of ~3 kWh per hour away). When connected and charging, the EV acts as a consumption device.
Consumption devices (AC, Heater) should have realistic wattage ranges and vary somewhat over time (not just flat values).
Store the computed results in Redis, structured for efficient retrieval by the energyStats query. Choose a key structure that makes sense for your design.

Deliverables
1. Source Code Repository
Clean, well-organized Django project on GitHub.
2. Docker Setup
docker-compose.yml and Dockerfile(s) that bring up the full stack (Django, PostgreSQL, Redis, Celery) with a single command.
3. README
Setup instructions, example API requests, and any decisions worth noting.
4. Design Document
A short written document covering:
Data model rationale: Why you chose your modeling approach for devices and the EV dual-role problem. What alternatives did you consider?
Simulation design: How your simulation pipeline works, what assumptions you made, and where it would break down or need changes for production use.
Scaling considerations: If this system needed to support 10,000 users with 50 devices each, what would break first? What would you change?
Known limitations: What would you improve given more time?

