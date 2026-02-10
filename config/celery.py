import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('smart_home_energy')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure Celery Beat schedule
app.conf.beat_schedule = {
    'run-energy-simulation-every-60-seconds': {
        'task': 'apps.simulation.tasks.run_energy_simulation',
        'schedule': 60.0,  # Run every 60 seconds
    },
}

app.conf.timezone = 'UTC'
