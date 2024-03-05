import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitoring_tasks.settings')

app = Celery('monitoring_tasks')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# celery beat tasks

app.conf.beat_schedule = {
    'count-outgoing-task-to-sign': {
        'task': 'ToDo_tasks.tasks.check_count_task_to_sign',
        'schedule': crontab(day_of_week='sunday', minute=0, hour=2)
    },
    'count-task-to-need-approve': {
        'task': 'ToDo_tasks.tasks.check_count_need_approve',
        'schedule': crontab(day_of_week='sunday', minute=0, hour=2)
    },
    'count-task-incoming-to-sing': {
        'task': 'ToDo_tasks.tasks.check_count_task_incoming_to_sign',
        'schedule': crontab(day_of_week='sunday', minute=0, hour=2)
    },
    'count-task-workers-to-sing': {
        'task': 'ToDo_tasks.tasks.check_count_task_workers_to_sign',
        'schedule': crontab(day_of_week='sunday', minute=0, hour=2)
    },
    'count-task-unread-inbox': {
        'task': 'ToDo_tasks.tasks.check_count_unread_inbox',
        'schedule': crontab(day_of_week='sunday', minute=0, hour=2)
    },
    'count-task-need-change': {
        'task': 'ToDo_tasks.tasks.check_count_change_my_tasks',
        'schedule': crontab(day_of_week='sunday', minute=0, hour=2)
    },
    'drafts-need-delete': {
        'task': 'ToDo_tasks.tasks.check_drafts',
        'schedule': crontab(minute=0, hour=3)
    },


}

