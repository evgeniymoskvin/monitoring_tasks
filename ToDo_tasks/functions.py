from .models import Employee, TaskModel, ContractModel, ObjectModel, StageModel
from .forms import TaskForm, TaskCheckForm


def get_signature_info(obj) -> dict:
    """
    Функция пытается проверить корректно ли указаны авторы в подписях
    В случае если какой-то из авторов был заполнен с ошибкой, везде возвращает None
    :param obj: Queryset
    :return: словарь со значениями
    """
    try:
        signature_info = {
            "first_sign_name": f'{obj.first_sign_user.first_name[:1]}. {obj.first_sign_user.middle_name[:1]}. {obj.first_sign_user.last_name}',
            "first_sign_job_title": obj.first_sign_user.job_title.job_title,
            "second_sign_name": f'{obj.second_sign_user.first_name[:1]}. {obj.second_sign_user.middle_name[:1]}. {obj.second_sign_user.last_name}',
            "second_sign_job_title": obj.second_sign_user.job_title.job_title,
            "cpe_sign_name": f'{obj.cpe_sign_user.first_name[:1]}. {obj.cpe_sign_user.middle_name[:1]}. {obj.cpe_sign_user.last_name}',
            "cpe_sign_job_title": obj.cpe_sign_user.job_title.job_title}
    except AttributeError:
        signature_info = {"first_sign_name": f'None',
                          "first_sign_job_title": f'None',
                          "second_sign_name": f'None',
                          "second_sign_job_title": f'None',
                          "cpe_sign_name": f'None',
                          "cpe_sign_job_title": f'None'}
    return signature_info


def get_data_for_form(obj):
    author = Employee.objects.get(id=obj.author_id)
    data = {"text_task": obj.text_task,
            "author": f'{author.first_name[:1]}. {author.middle_name[:1]}. {author.last_name}',
            "task_object": str(obj.task_object),
            "task_order": obj.task_order,
            "task_contract": str(obj.task_contract.contract_name),
            "task_stage": str(obj.task_stage.stage_name)}
    return data