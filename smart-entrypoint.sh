#!/bin/bash
set -e

SERVICE_TYPE=${SERVICE_TYPE:-web}

echo "Starting service: $SERVICE_TYPE"

case $SERVICE_TYPE in
  web)
    exec bash /app/entrypoint.sh
    ;;
  celery-worker)
    exec bash /app/railway-celery-worker.sh
    ;;
  celery-beat)
    exec bash /app/railway-celery-beat.sh
    ;;
  *)
    echo "Unknown SERVICE_TYPE: $SERVICE_TYPE"
    exit 1
    ;;
esac
