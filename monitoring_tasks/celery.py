import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitoring_tasks.settings')

app = Celery('monitoring_tasks')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# celery beat tasks

app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'ToDo_tasks.tasks.write_spam_repeat',
        'schedule': crontab()
    },
}