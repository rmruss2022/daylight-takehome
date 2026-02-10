.PHONY: help build up down logs shell migrate createsuperuser seed test clean

help:
	@echo "Smart Home Energy Management System - Development Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  build         Build Docker images"
	@echo "  up            Start all services"
	@echo "  down          Stop all services"
	@echo "  restart       Restart all services"
	@echo "  logs          View logs (all services)"
	@echo "  logs-web      View web service logs"
	@echo "  logs-celery   View celery logs"
	@echo "  logs-beat     View celery-beat logs"
	@echo "  shell         Open Django shell"
	@echo "  migrate       Run database migrations"
	@echo "  makemigrations Create new migrations"
	@echo "  createsuperuser Create Django superuser"
	@echo "  seed          Seed database with test data"
	@echo "  test          Run tests"
	@echo "  test-cov      Run tests with coverage"
	@echo "  clean         Stop services and remove volumes"
	@echo "  reset         Clean build and start fresh"
	@echo "  verify        Verify project structure"

build:
	docker compose build

up:
	docker compose up

up-d:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

logs-web:
	docker compose logs -f web

logs-celery:
	docker compose logs -f celery

logs-beat:
	docker compose logs -f celery-beat

shell:
	docker compose exec web python manage.py shell

migrate:
	docker compose exec web python manage.py migrate

makemigrations:
	docker compose exec web python manage.py makemigrations

createsuperuser:
	docker compose exec web python manage.py createsuperuser

seed:
	docker compose exec web python manage.py seed_devices

test:
	docker compose exec web pytest

test-cov:
	docker compose exec web pytest --cov=apps --cov-report=html

clean:
	docker compose down -v

reset: clean build up-d migrate seed
	@echo "System reset complete! Run 'make createsuperuser' to create admin user."

verify:
	python verify_project.py

# Quick setup for first time
setup: build up-d
	@echo "Waiting for services to start..."
	@sleep 10
	@echo "Running migrations..."
	@make migrate
	@echo ""
	@echo "Setup complete! Next steps:"
	@echo "1. make createsuperuser"
	@echo "2. make seed"
	@echo "3. Visit http://localhost:8000/graphql"
