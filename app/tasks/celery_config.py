"""Celery configuration and beat schedule."""
from celery.schedules import crontab
from app.tasks.outbox_worker import celery_app

# Celery Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    'process-outbox-events': {
        'task': 'app.tasks.outbox_worker.process_outbox_events',
        'schedule': 30.0,  # Run every 30 seconds
        # Alternative: crontab(minute='*/1') for every minute
    },
    'expire-quotes': {
        'task': 'app.tasks.email_tasks.expire_quotes_task',
        'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
    },
    'expire-promotional-prices': {
        'task': 'app.tasks.pricing_tasks.expire_promotional_prices',
        'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
    },
}

celery_app.conf.timezone = 'UTC'

