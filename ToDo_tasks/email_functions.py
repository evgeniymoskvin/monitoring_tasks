import os

from django.core.mail import EmailMessage

from .models import Employee, TaskModel, ContractModel, ObjectModel, StageModel, TaskNumbersModel, CommandNumberModel, \
    CpeModel, CanAcceptModel, WorkerModel, ApproveModel, AttachmentFilesModel
from dotenv import load_dotenv

load_dotenv()
LINK_FOR_EMAIL = os.getenv('LINK_FOR_EMAIL')


def email_create_task(new_post, approved_user_list):
    """Функция рассылки почты при создании задания"""
    number_id = TaskModel.objects.get(task_number=new_post.task_number).id
    #  Отправка сообщения автору
    email_author = EmailMessage(f'Задание {new_post.task_number} создано',
                                f'Задание {new_post.task_number} создано, посмотрите {LINK_FOR_EMAIL}/details/{number_id}',
                                to=[new_post.author.user.email])
    try:
        email_author.send()
    except:
        print('Error send email')

    #  Отправка сообщения согласователям
    for approve_user_id in approved_user_list:
        email_approve = EmailMessage(f'Согласование задания {new_post.task_number}.',
                                     f'{Employee.objects.get(id=approve_user_id)}, задание {new_post.task_number} зарегистрировано в системе. Прошу рассмотреть и согласовать его. \n Посмотрите {LINK_FOR_EMAIL}/approve_details/{number_id}',
                                     to=[Employee.objects.get(id=approve_user_id).user.email])
        try:
            email_approve.send()
        except:
            print('Error send email')

    #  Отправка письма первому руководителю
    email_first_sign = EmailMessage(f'Подписание задания {new_post.task_number}.',
                                    f'{new_post.first_sign_user}, задание {new_post.task_number} зарегистрировано в системе. Прошу рассмотреть и подписать его. \n Посмотрите {LINK_FOR_EMAIL}/details_to_sign/{number_id}',
                                    to=[new_post.first_sign_user.user.email])
    try:
        email_first_sign.send()
    except:
        print('Error send email')

    #  Отправка сообщения второму руководителю
    email_second_sign = EmailMessage(f'Подписание задания {new_post.task_number}.',
                                     f'{new_post.second_sign_user}. задание {new_post.task_number} зарегистрировано в системе. Прошу рассмотреть и подписать его. \n Посмотрите {LINK_FOR_EMAIL}/details_to_sign/{number_id}',
                                     to=[new_post.second_sign_user.user.email])
    try:
        email_second_sign.send()
    except:
        print('Error send email')


def check_and_send_to_cpe(pk):
    """Отправка сообщения ГИП-у"""
    task = TaskModel.objects.get(id=pk)
    if (task.first_sign_status is True) and (task.second_sign_status is True) and (task.task_approved is True):
        cpe_in_object = CpeModel.objects.get_queryset().filter(cpe_object=task.task_object)
        cpe_list = []
        for cpe_ in cpe_in_object:
            cpe_list.append(cpe_.cpe_user)
        for cpe_for_email in cpe_list:
            email_cpe = EmailMessage(f'Подписание задания {task.task_number}.',
                                     f'{cpe_for_email}. задание {task.task_number} зарегистрировано в системе. Прошу рассмотреть и подписать его. \n Посмотрите {LINK_FOR_EMAIL}/details_to_sign/{task.id}',
                                     to=[cpe_for_email.user.email])
            try:
                email_cpe.send()
            except:
                print('Error send email')


def email_after_cpe_sign(pk):
    """Отправка сообщения принимающим, после подписания ГИП-ом"""
    task = TaskModel.objects.get(id=pk)
    if task.cpe_sign_status is True:
        #  Получаем список кому отправить письмо (кто имеет право подписывать)
        can_sign_users = CanAcceptModel.objects.get_queryset().filter(dep_accept=task.incoming_dep)
        incom_users_list = []
        for incom_user in can_sign_users:
            incom_users_list.append(incom_user.user_accept)
        for incoming_user in incom_users_list:
            # Отправка сообщения всем, кто может подписывать задание в отделе
            if task.cpe_comment:
                email_incoming = EmailMessage(f'Направлено задание  {task.task_number}.',
                                              f'{incoming_user}, Вам направлено задание {task.task_number}. Прошу рассмотреть и принять в работу. \n Посмотрите {LINK_FOR_EMAIL}/incoming_to_sign_details/{task.id}. \nКомментарий ГИп-а {task.cpe_comment}',
                                              to=[incoming_user.user.email])
            else:
                email_incoming = EmailMessage(f'Направлено задание  {task.task_number}.',
                                              f'{incoming_user}, Вам направлено задание {task.task_number}. Прошу рассмотреть и принять в работу. \n Посмотрите {LINK_FOR_EMAIL}/incoming_to_sign_details/{task.id}.',
                                              to=[incoming_user.user.email])
            try:
                email_incoming.send()
            except:
                print('Error send email')

        # Отправка сообщения автору, о том что все подписано
        email_author = EmailMessage(f'Задание {task.task_number} подписано',
                                    f'Задание {task.task_number} подписано. \nПосмотрите {LINK_FOR_EMAIL}/details/{task.id}',
                                    to=[task.author.user.email])
        try:
            email_author.send()
        except:
            print('Error send email')


def add_worker_email(pk, worker_id):
    task = TaskModel.objects.get(id=pk)
    worker = Employee.objects.get(id=worker_id)
    email_to_worker = EmailMessage(f'Направлено задание  {task.task_number}.',
                                   f'{worker}, Вы назначены ответственным исполнителем по заданию {task.task_number}. Прошу принять в работу. '
                                   f'\nПосмотрите {LINK_FOR_EMAIL}/details/{task.id}. \nКомментарий ГИп-а: {task.cpe_comment}',
                                   to=[worker.user.email])
    try:
        email_to_worker.send()
    except:
        print('Error send email')


def delete_worker_email(pk):
    worker = WorkerModel.objects.get(id=pk)
    task = worker.task
    email_to_worker = EmailMessage(f'Больше не ответственный по заданию {task.task_number}.',
                                   f'{worker.worker_user}, Вы больше не ответственный исполнитель по заданию {task.task_number}.'
                                   f'\nПосмотрите {LINK_FOR_EMAIL}/details/{task.id}',
                                   to=[worker.worker_user.user.email])
    try:
        email_to_worker.send()
    except:
        print('Error send email')


def incoming_sign_email(task, incoming_signer):
    email_to_author = EmailMessage(f'Задание {task.task_number} подписано принимающим отделом.',
                                   f'{incoming_signer} принял(а) Ваше задание {task.task_number} в отдел {task.incoming_dep}.'
                                   f'\nПосмотрите {LINK_FOR_EMAIL}/details/{task.id}',
                                   to=[task.author.user.email])
    try:
        email_to_author.send()
    except:
        print('Error send email')


def incoming_not_sign_email(pk, incoming_signer, comment, need_edit=False):
    task = TaskModel.objects.get(id=pk)
    str_need_edit = 'не требуется'
    if need_edit is True:
        str_need_edit = 'требуется'
    email_to_author = EmailMessage(f'Отказ в подписании задания {task.task_number}.',
                                   f'{task.task_number} не подписано.'
                                   f'\n{incoming_signer}: {comment}.'
                                   f'\nРедактирование задания {str_need_edit}.'
                                   f'\nПосмотрите {LINK_FOR_EMAIL}/details/{task.id}',
                                   to=[task.author.user.email])
    try:
        email_to_author.send()
    except:
        print('Error send email')


def email_not_sign(pk, comment, user, need_edit=False,):
    task = TaskModel.objects.get(id=pk)
    sign_user = Employee.objects.get(user=user)
    str_need_edit = 'не требуется'
    if need_edit is True:
        str_need_edit = 'требуется'
    email_to_author = EmailMessage(f'Отказ в подписании задания {task.task_number}.',
                                   f'{sign_user} не подписал(а) задание {task.task_number}.'
                                   f'\nКомментарий: {comment}.'
                                   f'\nРедактирование задания {str_need_edit}.'
                                   f'\nПосмотрите {LINK_FOR_EMAIL}/details/{task.id}',
                                   to=[task.author.user.email])
    try:
        email_to_author.send()
    except:
        print('Error send email')


def email_change_task(obj, approved_user_list):
    """Функция рассылки почты при создании задания"""
    number_id = TaskModel.objects.get(task_number=obj.task_number).id
    #  Отправка сообщения автору
    email_author = EmailMessage(f'Задание {obj.task_number} отредактировано',
                                f'Задание {obj.task_number} отредактировано, посмотрите {LINK_FOR_EMAIL}/details/{number_id}',
                                to=[obj.author.user.email])
    try:
        email_author.send()
    except:
        print('Error send email')

    #  Отправка сообщения согласователям
    for approve_user_id in approved_user_list:
        email_approve = EmailMessage(f'Согласование задания {obj.task_number}.',
                                     f'{approve_user_id.approve_user}, задание {obj.task_number} отредактировано. Прошу рассмотреть и согласовать его. \n Посмотрите {LINK_FOR_EMAIL}/approve_details/{number_id}',
                                     to=[approve_user_id.approve_user.user.email])
        try:
            email_approve.send()
        except:
            print('Error send email')

    #  Отправка письма первому руководителю
    email_first_sign = EmailMessage(f'Подписание задания {obj.task_number}.',
                                    f'{obj.first_sign_user}, задание {obj.task_number} отредактировано. Прошу рассмотреть и подписать его. \n Посмотрите {LINK_FOR_EMAIL}/details_to_sign/{number_id}',
                                    to=[obj.first_sign_user.user.email])
    try:
        email_first_sign.send()
    except:
        print('Error send email')

    #  Отправка сообщения второму руководителю
    email_second_sign = EmailMessage(f'Подписание задания {obj.task_number}.',
                                     f'{obj.second_sign_user}. задание {obj.task_number} отредактировано. Прошу рассмотреть и подписать его. \n Посмотрите {LINK_FOR_EMAIL}/details_to_sign/{number_id}',
                                     to=[obj.second_sign_user.user.email])
    try:
        email_second_sign.send()
    except:
        print('Error send email')


def email_add_approver(pk, approve_user_id):
    task = TaskModel.objects.get(id=pk)
    emp_approve = Employee.objects.get(id=approve_user_id)
    email_to_approver = EmailMessage(f'Согласование задания {task.task_number}',
                                     f'{emp_approve}, задание {task.task_number} ждет вашего согласования.'
                                     f'\nПосмотрите {LINK_FOR_EMAIL}/approve_details/{task.id}',
                                     to=[emp_approve.user.email]
                                     )
    try:
        email_to_approver.send()
    except:
        print('Error send email')


def approve_give_comment_email(pk, user, text_comment):
    obj = TaskModel.objects.get(id=pk)
    email_to_author = EmailMessage(f'Согласователь прислал комментарий к заданию {obj.task_number}.',
                                     f'{obj.author}. '
                                     f'\n{Employee.objects.get(user=user)} прислал комментарий к заданию  {obj.task_number} '
                                     f'\nКомментарий: {text_comment}'
                                     f'\nПосмотрите {LINK_FOR_EMAIL}/details/{obj.id}',
                                   to=[obj.author.user.email])
    try:
        email_to_author.send()
    except:
        print('Error send email')


