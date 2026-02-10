#!/bin/bash
# Celery Beat Scheduler Start Script for Railway

# Wait for Redis to be ready
echo "Waiting for Redis..."
until python -c "import redis; r = redis.from_url('$REDIS_URL'); r.ping()" 2>/dev/null; do
  echo "Redis is unavailable - sleeping"
  sleep 1
done

# Wait for database to be ready
echo "Waiting for database..."
until python -c "import psycopg; psycopg.connect('$DATABASE_URL')" 2>/dev/null; do
  echo "Database is unavailable - sleeping"
  sleep 1
done

echo "Redis and Database are ready - starting Celery beat scheduler"
celery -A config beat --loglevel=info
