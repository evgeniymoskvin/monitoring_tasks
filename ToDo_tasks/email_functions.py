from django.core.mail import EmailMessage

from .models import Employee, TaskModel, ContractModel, ObjectModel, StageModel, TaskNumbersModel, CommandNumberModel, \
    CpeModel, CanAcceptModel, WorkerModel, ApproveModel, AttachmentFilesModel


def email_create_task(new_post, approved_user_list):
    number_id = TaskModel.objects.get(task_number=new_post.task_number).id
    email_author = EmailMessage(f'Задание {new_post.task_number} создано',
                         f'Задание {new_post.task_number} создано, посмотрите /details/{number_id}',
                         to=[new_post.author.user.email])
    email_author.send()

    for approve_user_id in approved_user_list:
        email_approve = EmailMessage(f'Задание {new_post.task_number} ожидает вашего согласования',
                             f'{Employee.objects.get(id=approve_user_id)}, {new_post.author} выдал задание {new_post.task_number} и оно ожидает Вашего согласования, посмотрите /details/{number_id}',
                             to=[Employee.objects.get(id=approve_user_id).user.email])
        email_approve.send()


    email_first_sign = EmailMessage(f'Задание {new_post.task_number} ожидает вашей подписи',
                         f'{new_post.first_sign_user}. {new_post.author} выдал задание {new_post.task_number} и оно ожидает Вашей подписи. Посмотрите /details/{number_id}',
                         to=[new_post.first_sign_user.user.email])
    email_first_sign.send()

    email_second_sign = EmailMessage(f'Задание {new_post.task_number} ожидает вашей подписи',
                                    f'{new_post.second_sign_user}. {new_post.author} выдал задание {new_post.task_number} и оно ожидает Вашей подписи. Посмотрите /details/{number_id}',
                                    to=[new_post.second_sign_user.user.email])
    email_second_sign.send()

