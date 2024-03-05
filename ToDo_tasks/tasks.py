import os
import datetime
import time
from django.core.mail import EmailMessage
from dotenv import load_dotenv

from .email_functions import email_create_task, check_variable_number, check_variable_outgoing_number, \
    check_variable_inbox_number, check_variable_my_inbox_number
from .models import Employee, ApproveModel, CanAcceptModel, TaskModel, WorkerModel, CanChangeWorkersModel, \
    DraftTaskModel
from .functions import get_list_to_sign, get_list_to_sign_cpe, get_list_incoming_tasks_to_sign
from monitoring_tasks.celery import app

load_dotenv()
LINK_FOR_EMAIL = os.getenv('LINK_FOR_EMAIL')


@app.task()
def celery_email_create_task(new_post_id, approved_user_list):
    email_create_task(new_post_id, approved_user_list)
    print('email_create_task')
    return f'Задание id={new_post_id} создано, рассылка сотрудникам сделана'


@app.task()
def check_count_task_to_sign():
    """Автоматическая рассылка писем, подписания исходящих заданий"""
    users = Employee.objects.get_queryset().filter(work_status=True)
    # Счетчики
    count_email_need_send_users = 0
    count_email_send_users = 0
    count_email_send_users_error = 0
    all_count = 0
    for user in users:
        if user.right_to_sign is True and user.cpe_flag is False:
            # Проверка для руководителей
            count_tasks = len(get_list_to_sign(user))
            all_count += count_tasks
            if count_tasks > 0:
                count_email_need_send_users += 1
                email_sign = EmailMessage(f'Исходящие задания ожидают подписи',
                                          f'{user}! {count_tasks} {check_variable_outgoing_number(count_tasks)} подписи. \n {LINK_FOR_EMAIL}/outgoing_to_sign/',
                                          to=[user.user.email])
                try:
                    time.sleep(1)
                    email_sign.send()
                    count_email_send_users += 1
                except Exception as e:
                    print(f'Error send email: {e}')
                    count_email_send_users_error += 1
        if user.cpe_flag is True:
            # Проверка для ГИП-ов
            count_tasks = get_list_to_sign_cpe(user).count()
            all_count += count_tasks
            if count_tasks > 0:
                count_email_need_send_users += 1
                email_sign = EmailMessage(f'Исходящие задания ожидают подписи',
                                          f'{user}! {count_tasks} {check_variable_outgoing_number(count_tasks)} подписи. \n {LINK_FOR_EMAIL}/outgoing_to_sign/',
                                          to=[user.user.email])
                try:
                    time.sleep(1)
                    email_sign.send()
                    count_email_send_users += 1
                except Exception as e:
                    print(f'Error send email: {e}')
                    count_email_send_users_error += 1
    return f'Всего требуется исходящих подписей: {all_count}. Требовалось отправить {count_email_need_send_users}. Отправилось: {count_email_send_users}. Ошибок: {count_email_send_users_error}'


@app.task()
def check_count_need_approve():
    """Автоматическая рассылка писем, требующих согласования задания"""
    users = Employee.objects.get_queryset().filter(work_status=True)
    # Счетчики
    count_email_need_send_users = 0
    count_email_send_users = 0
    count_email_send_users_error = 0
    all_count = 0
    for user in users:
        tasks_to_approve = ApproveModel.objects.get_queryset().filter(approve_user_id=user.id).filter(
            approve_status=False).count()
        all_count += tasks_to_approve
        if tasks_to_approve > 0:
            count_email_need_send_users += 1
            email_sign = EmailMessage(f'Задания ожидают согласования',
                                      f'{user}! Требуется согласовать {tasks_to_approve} {check_variable_number(tasks_to_approve)}. \n {LINK_FOR_EMAIL}/approve_list_to_sign/',
                                      to=[user.user.email])
            try:
                time.sleep(1)
                email_sign.send()
                count_email_send_users += 1
            except Exception as e:
                print(f'Error send email: {e}')
                count_email_send_users_error += 1
    return f'Всего требуются согласований: {all_count}. Требовалось отправить {count_email_need_send_users} писем. Отправилось: {count_email_send_users}. Ошибок: {count_email_send_users_error}'


@app.task()
def check_count_task_incoming_to_sign():
    """Автоматическая рассылка писем, требующих подписи входящих задания"""
    users = Employee.objects.get_queryset().filter(work_status=True)
    # Счетчики
    count_email_need_send_users = 0
    count_email_send_users = 0
    count_email_send_users_error = 0
    all_count = 0
    for user in users:
        if user.right_to_sign is True and user.cpe_flag is False:
            count_tasks = get_list_incoming_tasks_to_sign(user).count()
            all_count += count_tasks
            if count_tasks > 0:
                count_email_need_send_users += 1
                email_sign = EmailMessage(f'Входящие задания ожидают подписи',
                                          f'{user}! {count_tasks} {check_variable_inbox_number(count_tasks)} подписи. \n {LINK_FOR_EMAIL}/incoming_to_sign/',
                                          to=[user.user.email])
                try:
                    time.sleep(1)
                    email_sign.send()
                    count_email_send_users += 1
                except Exception as e:
                    print(f'Error send email: {e}')
                    count_email_send_users_error += 1
    return f'Всего не подписанных входящих: {all_count}. Требовалось отправить {count_email_need_send_users} писем. Отправилось: {count_email_send_users}. Ошибок: {count_email_send_users_error}'


@app.task()
def check_count_task_workers_to_sign():
    """Автоматическая рассылка писем, требующих назначения исполнителей"""
    users = Employee.objects.get_queryset().filter(work_status=True)
    # Счетчики
    count_email_need_send_users = 0
    count_email_send_users = 0
    count_email_send_users_error = 0
    for user in users:
        if user.right_to_sign is True and user.cpe_flag is False:
            if user.right_to_sign is True and user.cpe_flag is False:
                # Если надо указать все задания, где надо назначит исполнителей, активировать строчки
                queryset = CanChangeWorkersModel.objects.get_queryset().filter(user_accept=user)
                list_departments = []
                for dep in queryset:
                    list_departments.append(dep.dep_accept_id)
                count_tasks = TaskModel.objects.get_queryset().filter(incoming_dep_id__in=list_departments).filter(
                    incoming_status=True).filter(task_workers=False).count()
                # Если надо указать все задания, где надо назначит исполнителей, следующую строчку закомментировать
                # count_tasks = TaskModel.objects.get_queryset().filter(task_status=2).filter(
                #     incoming_dep=user.department).filter(task_workers=False).count()
                if count_tasks > 0:
                    count_email_need_send_users += 1
                    email_sign = EmailMessage(f'Необходимо назначить исполнителей',
                                              f'{user}! {count_tasks} {check_variable_number(count_tasks)} ждут назначение исполнителей. \n {LINK_FOR_EMAIL}/incoming_to_workers/',
                                              to=[user.user.email])
                    try:
                        time.sleep(1)
                        email_sign.send()
                        count_email_send_users += 1
                    except Exception as e:
                        print(f'Error send email: {e}')
                        count_email_send_users_error += 1
    return f'Всего требовалось назначить исполнителей: {count_email_need_send_users}. Отправилось: {count_email_send_users}. Ошибок: {count_email_send_users_error}'


@app.task()
def check_count_unread_inbox():
    """Автоматическая рассылка писем о непрочитанных заданиях"""
    users = Employee.objects.get_queryset().filter(work_status=True)
    # Счетчики
    count_email_need_send_users = 0
    count_email_send_users = 0
    count_email_send_users_error = 0
    all_count = 0
    for user in users:
        tasks_count_unread = WorkerModel.objects.get_queryset().filter(worker_user=user).filter(
            read_status=False).count()
        all_count += tasks_count_unread
        if tasks_count_unread > 0:
            count_email_need_send_users += 1
            email_sign = EmailMessage(f'Есть непрочитанные задания',
                                      f'{user}! {tasks_count_unread} {check_variable_my_inbox_number(tasks_count_unread)} просмотра. \n {LINK_FOR_EMAIL}/inbox/',
                                      to=[user.user.email])
            try:
                time.sleep(1)
                email_sign.send()
                count_email_send_users += 1
            except Exception as e:
                print(f'Error send email: {e}')
                count_email_send_users_error += 1
    return f'Всего непрочитанных зданий: {all_count}. Требовалось отправить {count_email_need_send_users} писем. Отправилось: {count_email_send_users}. Ошибок: {count_email_send_users_error}'


@app.task()
def check_count_change_my_tasks():
    """Автоматическая рассылка писем о заданиях требующих изменений"""
    users = Employee.objects.get_queryset().filter(work_status=True)
    # Счетчики
    count_email_need_send_users = 0
    count_email_send_users = 0
    count_email_send_users_error = 0
    all_count = 0
    for user in users:
        tasks_id_change = TaskModel.objects.get_queryset().filter(author=user).filter(task_status=1).filter(
            back_to_change=True).count()
        all_count += tasks_id_change
        if tasks_id_change > 0:
            count_email_need_send_users += 1
            email_sign = EmailMessage(f'Есть задания, требующие изменений',
                                      f'{user}! {tasks_id_change} {check_variable_number(tasks_id_change)} исправления. \n {LINK_FOR_EMAIL}/my_tasks_on_sign/',
                                      to=[user.user.email])
            try:
                time.sleep(1)
                email_sign.send()
                count_email_send_users += 1
            except Exception as e:
                print(f'Error send email: {e}')
                count_email_send_users_error += 1
    return f'Всего зданий требующих исправлений: {all_count}. Требовалось отправить {count_email_need_send_users} писем. Отправилось: {count_email_send_users}. Ошибок: {count_email_send_users_error}'


@app.task()
def check_drafts():
    """
    Проверка черновиков, удалять те, которые старше 30 дней
    """
    users = Employee.objects.get_queryset().filter(work_status=True)
    count_drafts = 0
    count_delete_drafts = 0
    today = datetime.date.today()
    for user in users:
        drafts = DraftTaskModel.objects.get_queryset().filter(author=user)
        for draft in drafts:
            draft_date = draft.draft_create_date.date()
            draft_delta = (today - draft_date).days
            count_drafts += 1
            if draft_delta > 30:
                count_delete_drafts += 1
                draft.delete()
    return f'Всего проверено {count_drafts} черновиков. Удалено {count_delete_drafts} черновиков'
