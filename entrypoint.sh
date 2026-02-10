#!/bin/bash
set -e

echo "Starting Daylight Energy Management System..."

# Wait for database to be ready
echo "Waiting for database..."
while ! pg_isready -h ${POSTGRES_HOST:-db} -p ${POSTGRES_PORT:-5432} -U ${POSTGRES_USER:-postgres} > /dev/null 2>&1; do
  echo "Database is unavailable - sleeping"
  sleep 1
done

echo "Database is up - executing migrations"

# Run migrations
python manage.py migrate --noinput

# Create or update superuser
python manage.py shell << END
from django.contrib.auth import get_user_model
import os

User = get_user_model()
username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin')

try:
    admin_user = User.objects.get(username=username)
    admin_user.set_password(password)
    admin_user.save()
    print(f'Superuser {username} password updated.')
except User.DoesNotExist:
    User.objects.create_superuser(username, email, password)
    print(f'Superuser {username} created successfully!')
END

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 4 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
