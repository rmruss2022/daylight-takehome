#!/usr/bin/env python
"""Quick verification script to check project structure."""

import os
import sys

def check_file_exists(path, description):
    """Check if a file exists."""
    exists = os.path.exists(path)
    status = "✓" if exists else "✗"
    print(f"{status} {description}: {path}")
    return exists

def main():
    print("Verifying Smart Home Energy Management System project structure...\n")

    all_good = True

    # Core files
    print("Core Files:")
    all_good &= check_file_exists("manage.py", "Django manage script")
    all_good &= check_file_exists("requirements.txt", "Requirements file")
    all_good &= check_file_exists("Dockerfile", "Dockerfile")
    all_good &= check_file_exists("docker-compose.yml", "Docker Compose")
    all_good &= check_file_exists(".env", "Environment file")
    all_good &= check_file_exists("README.md", "README")
    all_good &= check_file_exists("DESIGN.md", "Design doc")

    print("\nConfig:")
    all_good &= check_file_exists("config/__init__.py", "Config init")
    all_good &= check_file_exists("config/settings/base.py", "Base settings")
    all_good &= check_file_exists("config/celery.py", "Celery config")
    all_good &= check_file_exists("config/urls.py", "URL config")

    print("\nDevice Models:")
    all_good &= check_file_exists("apps/devices/models/base.py", "Base device model")
    all_good &= check_file_exists("apps/devices/models/production.py", "Production models")
    all_good &= check_file_exists("apps/devices/models/storage.py", "Storage models")
    all_good &= check_file_exists("apps/devices/models/consumption.py", "Consumption models")
    all_good &= check_file_exists("apps/devices/admin.py", "Admin config")

    print("\nGraphQL API:")
    all_good &= check_file_exists("apps/api/schema.py", "GraphQL schema")
    all_good &= check_file_exists("apps/api/permissions.py", "Permissions")
    all_good &= check_file_exists("apps/api/mutations/auth.py", "Auth mutations")
    all_good &= check_file_exists("apps/api/mutations/device.py", "Device mutations")
    all_good &= check_file_exists("apps/api/queries/device.py", "Device queries")
    all_good &= check_file_exists("apps/api/queries/energy.py", "Energy queries")

    print("\nSimulation:")
    all_good &= check_file_exists("apps/simulation/redis_client.py", "Redis client")
    all_good &= check_file_exists("apps/simulation/tasks.py", "Celery tasks")
    all_good &= check_file_exists("apps/simulation/simulators/solar.py", "Solar simulator")
    all_good &= check_file_exists("apps/simulation/simulators/battery.py", "Battery simulator")
    all_good &= check_file_exists("apps/simulation/simulators/ev.py", "EV simulator")

    print("\nTests:")
    all_good &= check_file_exists("tests/conftest.py", "Test config")
    all_good &= check_file_exists("tests/test_devices/test_models.py", "Model tests")
    all_good &= check_file_exists("tests/test_simulation/test_simulators.py", "Simulator tests")
    all_good &= check_file_exists("tests/test_api/test_auth.py", "Auth tests")

    print("\nManagement Commands:")
    all_good &= check_file_exists("apps/devices/management/commands/seed_devices.py", "Seed command")

    print("\n" + "="*60)
    if all_good:
        print("✓ All required files are present!")
        print("\nNext steps:")
        print("1. docker compose up --build")
        print("2. docker compose exec web python manage.py migrate")
        print("3. docker compose exec web python manage.py createsuperuser")
        print("4. docker compose exec web python manage.py seed_devices")
        print("5. Visit http://localhost:8000/graphql")
        return 0
    else:
        print("✗ Some files are missing. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
