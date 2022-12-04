from django import template
from django.shortcuts import render, redirect
from ..models import *
from ..views import IndexView
from ..functions import get_list_to_sign, get_list_to_sign_cpe, get_list_incoming_tasks_to_sign

register = template.Library()


@register.simple_tag()
def get_name(user):
    full_user = Employee.objects.get(user=user)
    return full_user


@register.simple_tag()
def get_count_task_to_sign(user):
    count_task_to_sign = ''
    if user.right_to_sign is True and user.cpe_flag is False:
        count_tasks = len(get_list_to_sign(user))
        if count_tasks > 0:
            count_task_to_sign = f'({count_tasks})'
    if user.cpe_flag is True:
        count_tasks = get_list_to_sign_cpe(user).count()
        if count_tasks > 0:
            count_task_to_sign = f'({count_tasks})'
    return count_task_to_sign


@register.simple_tag()
def get_count_task_incoming_to_sign(user):
    count_task_incoming_to_sign = ''
    if user.right_to_sign is True and user.cpe_flag is False:
        count_tasks = get_list_incoming_tasks_to_sign(user).count()
        if count_tasks > 0:
            count_task_incoming_to_sign = f'({count_tasks})'
    return count_task_incoming_to_sign

@register.simple_tag()
def get_count_task_workers_to_sign(user):
    count_task_to_workers = ''
    if user.right_to_sign is True and user.cpe_flag is False:
        count_tasks = TaskModel.objects.get_queryset().filter(task_status=2).filter(
                incoming_dep=user.department).filter(task_workers=False).count()
        if count_tasks > 0:
            count_task_to_workers = f'({count_tasks})'
    return count_task_to_workers

@register.simple_tag()
def unread_inbox(user):
    count_unread = ''
    tasks_count_unread = WorkerModel.objects.get_queryset().filter(worker_user=user).filter(read_status=False).count()
    if tasks_count_unread > 0:
        count_unread = f'({tasks_count_unread})'
    return count_unread



@register.simple_tag()
def need_approve(user):
    count_unread = ''
    tasks_to_approve = ApproveModel.objects.get_queryset().filter(approve_user_id=user.id).filter(approve_status=False).count()

    if tasks_to_approve > 0:
        count_unread = f'({tasks_to_approve})'
    return count_unread

@register.simple_tag()
def split_filename(value:str):
    return str(value).split('/')[-1]

# count_task_to_workers = ''
# count_task_incoming_to_sign = ''
# if user_ep.right_to_sign is True and user_ep.cpe_flag is False:
#     count_task_to_workers = TaskModel.objects.get_queryset().filter(task_status=2).filter(
#         incoming_dep=user.department).filter(task_workers=False).count()
#     count_task_incoming_to_sign = get_list_incoming_tasks_to_sign(user).count()
# content = {
#     # 'user': user,
#     "count_task_to_sign": f'({count_task_to_sign})',
#     "count_task_to_workers": f'({count_task_to_workers})',
#     "count_task_incoming_to_sign": f'({count_task_incoming_to_sign})'}
