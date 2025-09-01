import os
from celery import Celery

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_travel_app.settings')

# Create Celery app
app = Celery('alx_travel_app')

# Load settings from Django config using CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks from all registered apps
app.autodiscover_tasks()

