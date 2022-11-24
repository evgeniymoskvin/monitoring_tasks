from .models import Employee, TaskModel, CpeModel, ContractModel, ObjectModel, StageModel
from .forms import TaskForm, TaskCheckForm, TaskEditForm


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


def get_data_for_form(obj) -> dict:
    data = {
        "text_task": obj.text_task,
        "author": f'{obj.author}',
        "task_object": str(obj.task_object),
        "task_order": obj.task_order,
        "task_contract": str(obj.task_contract.contract_name),
        "task_stage": str(obj.task_stage.stage_name),
        "incoming_employee": str(obj.incoming_employee),
        "task_building": str(obj.task_building),
        "task_type_work": str(obj.get_task_type_work_display()),
    }
    return data


def get_data_for_detail(request, pk) -> dict:
    """Получение информации для формирования подробностей"""
    obj = TaskModel.objects.get(pk=pk)
    signature_info = get_signature_info(obj)  # получаем информацию о подписях
    task_status = obj.get_task_status_display

    data = get_data_for_form(obj)  # получаем данные для подгрузки в форму
    form = TaskCheckForm(initial=data)
    user = Employee.objects.get(user=request.user)
    return {
        'obj': obj,
        'user': user,
        'form': form,
        "sign_info": signature_info,
        "task_status": task_status,
    }


def get_list_to_sign(sign_user) -> list:
    """Получаем список заданий
    собираем все задания, где пользователь указан как первый подписант, затем как второй
    после чего формируем единый список без повторений"""
    # Получаем объекты по трем фильтрам: пользователь, не подписано, не возращено на исправление
    to_sign_objects_first = TaskModel.objects.get_queryset().filter(first_sign_user=sign_user.id).filter(
        first_sign_status=False).filter(back_to_change=False)
    to_sign_objects_second = TaskModel.objects.get_queryset().filter(second_sign_user=sign_user.id).filter(
        second_sign_status=False).filter(back_to_change=False)
    to_sign_objects_cpe = TaskModel.objects.get_queryset().filter(cpe_sign_user=sign_user.id).filter(
        cpe_sign_status=False).filter(first_sign_status=True).filter(second_sign_status=True).filter(
        back_to_change=False)
    # Формируем перебором список заданий
    sign_list = []
    for obj in to_sign_objects_first:
        if obj not in sign_list:
            sign_list.append(obj)
    for obj in to_sign_objects_second:
        if obj not in sign_list:
            sign_list.append(obj)
    for obj in to_sign_objects_cpe:
        if obj not in sign_list:
            sign_list.append(obj)
    return sign_list


def get_task_edit_form(request, obj):
    form = TaskEditForm(instance=obj)
    department_user = Employee.objects.get(user=request.user).department
    form.fields['first_sign_user'].queryset = Employee.objects.filter(department=department_user).filter(
        right_to_sign=True)  # получаем в 1ое поле список пользователей по двум фильтрам
    form.fields['second_sign_user'].queryset = Employee.objects.filter(department=department_user).filter(
        right_to_sign=True)  # получаем во 2ое поле список пользователей по двум фильтрам
    cpe_cpe = CpeModel.objects.get_queryset()
    list_cpe = []
    for objects in cpe_cpe:
        list_cpe.append(objects.cpe_user.id)
    form.fields["cpe_sign_user"].queryset = Employee.objects.get_queryset().filter(id__in=list_cpe)
    return form
