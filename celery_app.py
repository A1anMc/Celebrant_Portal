"""
Celery application configuration for the Celebrant Portal
"""
from celery import Celery
from flask import Flask
import os


def make_celery(app: Flask) -> Celery:
    """Create and configure Celery instance with Flask app context."""
    
    celery = Celery(app.import_name)
    
    # Configure Celery settings using new format
    celery.conf.update(
        # Broker and backend
        broker_url=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        result_backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        
        # Serialization
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        
        # Timezone and UTC
        timezone='Australia/Melbourne',
        enable_utc=True,
        
        # Task settings
        result_expires=3600,
        task_track_started=True,
        task_time_limit=30 * 60,  # 30 minutes
        task_soft_time_limit=25 * 60,  # 25 minutes
        
        # Worker settings
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=1000,
    )
    
    # Configure beat schedule for periodic tasks
    celery.conf.beat_schedule = {
        'check-form-deadlines': {
            'task': 'legal_forms_tasks.check_form_deadlines',
            'schedule': 3600.0,  # Every hour
        },
        'send-daily-reminders': {
            'task': 'legal_forms_tasks.send_daily_reminders',
            'schedule': 86400.0,  # Daily at midnight
        },
        'generate-weekly-reports': {
            'task': 'legal_forms_tasks.generate_compliance_report',
            'schedule': 604800.0,  # Weekly
        },
        'cleanup-old-alerts': {
            'task': 'legal_forms_tasks.cleanup_old_alerts',
            'schedule': 86400.0,  # Daily
        },
    }
    
    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context."""
        abstract = True
        
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery


# Create standalone Celery app for worker processes
def create_celery_app():
    """Create Celery app for standalone worker processes."""
    from config import Config
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    return make_celery(app)


# For worker processes
celery = create_celery_app() 