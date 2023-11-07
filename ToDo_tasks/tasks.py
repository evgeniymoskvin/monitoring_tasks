from .email_functions import text_spam, email_create_task
from monitoring_tasks.celery import app
import datetime
from django.core.mail import EmailMessage


@app.task()
def write_spam(text_to_spam):
    text_spam(text_to_spam)
    print('Work при открытии добавить задание')
    return True

@app.task()
def celery_email_create_task(new_post_id, approved_user_list):
    email_create_task(new_post_id, approved_user_list)
    print('email_create_task')
    return True

@app.task()
def write_spam_repeat():
    now = datetime.datetime.now()
    email_send = EmailMessage(f'Каждую минуту Celery', f'Время через Celery: {now}', to=['tttestttsait@yandex.ru'])
    try:
        email_send.send()
    except:
        print('Error send email')
    print(f'Сейчас')
    return True
