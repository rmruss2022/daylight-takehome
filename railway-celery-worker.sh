#!/bin/bash
# Celery Worker Start Script for Railway

# Wait for Redis to be ready
echo "Waiting for Redis..."
until python -c "import redis; r = redis.from_url('$REDIS_URL'); r.ping()" 2>/dev/null; do
  echo "Redis is unavailable - sleeping"
  sleep 1
done

echo "Redis is ready - starting Celery worker"
celery -A config worker --loglevel=info --concurrency=2
