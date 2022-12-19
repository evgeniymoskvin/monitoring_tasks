from django.shortcuts import redirect
from .models import Employee, TaskModel, CpeModel, ContractModel, ObjectModel, StageModel, CanAcceptModel
from .forms import TaskForm, TaskCheckForm, TaskEditForm, WorkerModel, ApproveModel, AttachmentFilesModel
from .email_functions import add_worker_email


def get_signature_info(obj) -> dict:
    """
    Функция пытается проверить корректно ли указаны авторы в подписях
    В случае если какой-то из авторов был заполнен с ошибкой, везде возвращает None
    :param obj: Queryset
    :return: словарь со значениями
    """
    signature_info = {}
    if obj.first_sign_user:
        signature_info[
            'first_sign_name'] = f'{obj.first_sign_user.first_name[:1]}. {obj.first_sign_user.middle_name[:1]}. {obj.first_sign_user.last_name}'
        signature_info['first_sign_job_title'] = obj.first_sign_user.job_title.job_title
    if obj.second_sign_user:
        signature_info[
            'second_sign_name'] = f'{obj.second_sign_user.first_name[:1]}. {obj.second_sign_user.middle_name[:1]}. {obj.second_sign_user.last_name}'
        signature_info['second_sign_job_title'] = obj.second_sign_user.job_title.job_title
    if obj.cpe_sign_user:
        signature_info[
            'cpe_sign_name'] = f'{obj.cpe_sign_user.first_name[:1]}. {obj.cpe_sign_user.middle_name[:1]}. {obj.cpe_sign_user.last_name}'
        signature_info['cpe_sign_job_title'] = obj.cpe_sign_user.job_title.job_title
    else:
        signature_info['cpe_sign_name'] = 'Не определен'
        signature_info['cpe_sign_job_title'] = 'ГИП'
    if obj.incoming_employee:
        signature_info[
            'incom_sign_name'] = f'{obj.incoming_employee.first_name[:1]}. {obj.incoming_employee.middle_name[:1]}. {obj.incoming_employee.last_name}'
        signature_info['incom_job_title'] = 'Принимающий'
    else:
        signature_info['incom_sign_name'] = 'Не определен'
        signature_info['incom_job_title'] = 'Принимающий'

    return signature_info


def get_data_for_form(obj) -> dict:
    data = {
        "text_task": obj.text_task,
        "author": f'{obj.author}',
        "task_object": str(obj.task_object),
        # "task_order": str(obj.task_order),
        # "task_contract": str(obj.task_contract.contract_name),
        # "task_stage": str(obj.task_stage),
        "incoming_dep": str(obj.incoming_dep),
        "task_building": str(obj.task_building),
        "task_type_work": str(obj.get_task_type_work_display()),
        "task_mark_doc": str(obj.task_mark_doc),

    }
    try:
        data["task_order"] = str(obj.task_order)
    except:
        data["task_order"] = str('-----')
    try:
        data['task_contract'] = str(obj.task_contract.contract_name)
    except:
        data['task_contract'] = str('-----')

    try:
        data['task_stage'] = str(obj.task_stage.stage_name)
    except:
        data['task_stage'] = str('-----')

    if obj.task_order is None:
        data['task_order'] = str('-----')

    return data


def get_data_for_detail(request, pk) -> dict:
    """Получение информации для формирования подробностей"""
    obj = TaskModel.objects.get(pk=pk)
    signature_info = get_signature_info(obj)  # получаем информацию о подписях
    task_status = obj.get_task_status_display

    data = get_data_for_form(obj)  # получаем данные для подгрузки в форму
    form = TaskCheckForm(initial=data)
    user = Employee.objects.get(user=request.user)
    approve_users = ApproveModel.objects.get_queryset().filter(approve_task_id=pk)
    workers = WorkerModel.objects.get_queryset().filter(task_id=pk)
    files = AttachmentFilesModel.objects.get_queryset().filter(task_id=pk)
    return {
        'obj': obj,
        'user': user,
        'form': form,
        "sign_info": signature_info,
        "task_status": task_status,
        "workers": workers,
        "approve_users": approve_users,
        "files": files
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


def get_list_to_sign_cpe(sign_user):
    """Функция возвращающая queryset из заданий, которые ожидают подписи ГИП-а"""
    # Получаем из таблицы CpeModel список объектов, где может подписываться данный пользователь
    objects_queryset = CpeModel.objects.get_queryset().filter(cpe_user=sign_user)
    # Формируем список id этих объектов
    list_objects = []
    for object in objects_queryset:
        list_objects.append(object.cpe_object_id)
    # Фильтруем задания: объект в списке, подписи ГИП-а нет, первый и второй пользователь подписали, не возвращено на доработку
    to_sign_objects_cpe = TaskModel.objects.get_queryset().filter(task_object__in=list_objects).filter(
        cpe_sign_status=False).filter(first_sign_status=True).filter(second_sign_status=True).filter(
        back_to_change=False).filter(task_approved=True)
    return to_sign_objects_cpe


def get_task_edit_form(request, obj):
    """Функция формирующая форму для редактирования задания"""
    form = TaskEditForm(instance=obj)
    # Получаем отдел пользователя
    department_user = Employee.objects.get(user=request.user).department
    # Оставляем только пользователей отдела с возможностью подписывать задания
    form.fields['first_sign_user'].queryset = Employee.objects.filter(department=department_user).filter(
        right_to_sign=True)  # получаем в 1ое поле список пользователей по двум фильтрам
    form.fields['second_sign_user'].queryset = Employee.objects.filter(department=department_user).filter(
        right_to_sign=True)  # получаем во 2ое поле список пользователей по двум фильтрам
    return form


def get_list_incoming_tasks_to_sign(sign_user):
    """Функция возвращает queryset входящих заданий требующих подписи"""
    # Получаем queryset того, что может подписывать пользователь
    queryset = CanAcceptModel.objects.get_queryset().filter(user_accept=sign_user)
    # Получаем список id этих отделов
    list_departments = []
    for dep in queryset:
        list_departments.append(dep.dep_accept_id)
    # Формируем queryset этих заданий: отдел в списке, ГИП подписал, статус принятия False
    return TaskModel.objects.get_queryset().filter(incoming_dep_id__in=list_departments).filter(
        cpe_sign_status=True).filter(incoming_status=False).filter(back_to_change=False)


def get_list_incoming_tasks_to_workers(sign_user):
    queryset = CanAcceptModel.objects.get_queryset().filter(user_accept=sign_user)
    list_departments = []
    for dep in queryset:
        list_departments.append(dep.dep_accept_id)
    return TaskModel.objects.get_queryset().filter(incoming_dep_id__in=list_departments).filter(
        incoming_status=True).filter(task_workers=False)


def get_list_to_change_workers(sign_user):
    queryset = CanAcceptModel.objects.get_queryset().filter(user_accept=sign_user)
    list_departments = []
    for dep in queryset:
        list_departments.append(dep.dep_accept_id)
    return TaskModel.objects.get_queryset().filter(incoming_dep_id__in=list_departments).filter(
        incoming_status=True)


def save_to_worker_list(request, pk):
    task = TaskModel.objects.get(id=pk)
    task.task_workers = True
    task.save()
    # Создаем объект таблицы Исполнители
    obj = WorkerModel()
    obj.task_id = pk
    obj.read_status = False  # Присваиваем флаг о не прочтении сообщения
    obj.worker_user_id = request.POST.get("worker_user")
    obj.save()
    add_worker_email(pk, request.POST.get("worker_user"))


def is_valid_queryparam(param):
    return param != '' and param is not None