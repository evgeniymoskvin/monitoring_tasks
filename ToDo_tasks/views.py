import datetime
import mimetypes
import os.path

from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.utils.encoding import escape_uri_path
from django.views import View
from django.db.models import Q
from django.conf import settings
from django.http import HttpResponse, Http404

from .models import Employee, TaskModel, ContractModel, ObjectModel, StageModel, TaskNumbersModel, CommandNumberModel, \
    CpeModel, CanAcceptModel, WorkerModel, ApproveModel, AttachmentFilesModel
from .forms import TaskForm, TaskEditForm, SearchForm, WorkerForm, WorkersEditForm, \
    TaskFormForSave, ApproveForm, FilesUploadForm, UserProfileForm, ApproveEditForm
from .functions import get_data_for_detail, get_list_to_sign, get_task_edit_form, \
    get_list_to_sign_cpe, get_list_incoming_tasks_to_sign, get_list_incoming_tasks_to_workers, save_to_worker_list, \
    get_list_to_change_workers, is_valid_queryparam
from .pdf_making import pdf_gen
from .email_functions import email_create_task, check_and_send_to_cpe, email_after_cpe_sign, delete_worker_email, \
    incoming_not_sign_email, email_not_sign, email_change_task, approve_give_comment_email, email_add_approver, \
    incoming_sign_email


class IndexView(View):
    """Главная страница"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        """
        Проверяет авторизацию пользователя и выводит данные на странице,
        либо redirect на страницу авторизации
        """

        # Получаем информацию о пользователе из таблицы Employee на основании request
        try:
            user = Employee.objects.get(user=request.user)
            content = {
                'user': user,
            }
            return render(request, 'todo_tasks/index.html', content)
        except:
            return redirect('edit_profile')

    def post(self, request):
        """post запрос со страницы поиска"""
        if request.POST.get('search_field') == '':
            return redirect(request.META['HTTP_REFERER'])
        else:
            return redirect(f'search_result', request.POST.get('search_field'))


class IssuedTasksView(View):
    """Страница выданных заданий отдела, уже всеми подписаны, принятых принимающим"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        user = Employee.objects.get(user=request.user)
        data_all = TaskModel.objects.get_queryset().filter(department_number=user.department).filter(
            ~Q(task_status=1)).filter(incoming_status=True)
        content = {'data_all': data_all,
                   'user': user}
        return render(request, 'todo_tasks/department_tasks/issued_tasks.html', content)


class OutgoingTasksView(View):
    """Страница исходящих заданий, которые еще на подписи"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        user = Employee.objects.get(user=request.user)
        data_to_sign = TaskModel.objects.get_queryset().filter(department_number=user.department).filter(task_status=1)
        content = {'data_to_sign': data_to_sign,
                   'user': user}
        return render(request, 'todo_tasks/department_tasks/outgoing_tasks.html', content)


class IncomingDepView(View):
    """Страница входящих заданий по номеру отделу пользователя"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        user = Employee.objects.get(user=request.user)  # Получаем пользователя из запроса
        user_dep = user.department_id  # получаем id номер отдела
        data_have_workers = TaskModel.objects.get_queryset().filter(incoming_dep=user_dep).filter(task_status=2)
        content = {'data_have_workers': data_have_workers,
                   'user': user}
        return render(request, 'todo_tasks/department_tasks/incoming_to_dep.html', content)


class UserTaskView(View):
    """Просмотр "мои выданные" заданий """

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        data_user = TaskModel.objects.get_queryset().filter(author__user=request.user).filter(task_status=2)
        user = Employee.objects.get(user=request.user)
        text_status = f"выданные"
        content = {'data_user': data_user,
                   'user': user,
                   "text_status": text_status}
        return render(request, 'todo_tasks/my_tasks/my_outgoing_tasks.html', content)


class UserTaskOnSignView(View):
    """Получение списка для страницы исходящих заданий"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        data_user = TaskModel.objects.get_queryset().filter(author__user=request.user).filter(task_status=1)
        user = Employee.objects.get(user=request.user)
        text_status = f"исходящие"
        content = {'data_user': data_user,
                   'user': user,
                   "text_status": text_status}
        return render(request, 'todo_tasks/my_tasks/my_outgoing_tasks.html', content)


class DetailView(View):
    """Формирование страницы просмотра деталей"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request, pk):
        """Получаем номер задания из ссылки и формируем страницу подробностей"""
        content = get_data_for_detail(request, pk)
        if TaskModel.objects.get(id=pk) in get_list_to_change_workers(content['user']):
            content['change_work_flag'] = True
        content[
            'flag'] = True  # Для того, что бы шестеренка была доступна только на странице деталей, и ни на каких других дочерних

        return render(request, 'todo_tasks/details/details.html', content)

    def post(self, request, pk):
        if 'cancel_modal_button' in request.POST:
            obj = TaskModel.objects.get(pk=pk)
            print(pk, ' cancel task')
            obj.task_status = 0
            print(obj)
            obj.save()
        if 'correction_modal_button' in request.POST:
            obj = TaskModel.objects.get(pk=pk)
            print(pk, ' correction task')
            obj.task_status = 3
            print(obj)
            obj.save()

        return redirect(request.META['HTTP_REFERER'])


class AddTaskView(View):
    """Добавление нового задания"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        form = TaskForm()  # Форма задания
        approve_form = ApproveForm()  # Форма согласователей
        approve_form.fields['approve_user'].queryset = Employee.objects.filter(cpe_flag=False)
        # Фильтруем поля руководителей в соответствии с отделом пользователя
        department_user = Employee.objects.get(user=request.user).department  # получаем номер отдела
        form.fields['first_sign_user'].queryset = Employee.objects.filter(department=department_user).filter(
            right_to_sign=True)  # получаем в 1ое поле список пользователей по двум фильтрам
        form.fields['second_sign_user'].queryset = Employee.objects.filter(department=department_user).filter(
            right_to_sign=True)  # получаем во 2ое поле список пользователей по двум фильтрам

        file_form = FilesUploadForm()
        objects = ObjectModel.objects.all()
        context = {'form': form,
                   "file_form": file_form,
                   'user': Employee.objects.get(user=request.user),
                   'objects': objects,
                   "approve_form": approve_form
                   }
        return render(request, 'todo_tasks/add_task/add_task.html', context)

    def post(self, request):
        # Создаем копию пост запроса, что бы можно было подменять свои значения
        temp_req = request.POST.copy()
        # Из исходного пост запроса получаем список отделов, куда надо выдать задания
        incoming_deps_list = request.POST.getlist('incoming_dep')
        approved_user_list = request.POST.getlist('approve_user')
        # Перебираем отделы в которые направляются задания
        for dep in incoming_deps_list:
            # Меняем значение отдела, на нужное нам из списка
            temp_req['incoming_dep'] = int(dep)
            # Грузим в форму для сохранения
            form = TaskFormForSave(temp_req)

            if form.is_valid():
                new_post = form.save(commit=False)  # отменяем отправку form в базу
                new_post.department_number = CommandNumberModel.objects.get(id=dep)  # Присваиваем отдел
                new_post.author = Employee.objects.get(user=request.user)  # добавляем пользователя из request
                new_post.department_number = new_post.author.department  # добавляем номер отдела пользователя, пока не знаю зачем
                # Получаем номер последнего задания из таблицы TaskNumbers
                last_number = TaskNumbersModel.objects.get(command_number=new_post.department_number)
                today_year = datetime.datetime.today().year  # выносим в отдельную переменную, что бы каждый раз не вызывалась функция
                # Проверяем год. Если отличается от нынешнего, обнуляем счетчик заданий
                if last_number.year_of_task == today_year:
                    last_number.count_of_task += 1
                else:
                    last_number.year_of_task = today_year
                    last_number.count_of_task = 1
                last_number.save()  # сохраняем в таблице счетчиков (TaskNumbersModel) обновленные данные
                if new_post.task_need_approve is False:
                    new_post.task_approved = True
                new_post.task_last_edit = datetime.datetime.now()  # Присваиваем дату последнего изменения

                new_post.task_number = f'ЗД-{new_post.department_number.command_number}-{last_number.count_of_task}-{str(today_year)[2:4]}'
                new_post.task_change_number = 0  # номер изменения присваиваем 0
                # print(new_post.task_number)
                form.save()  # сохраняем форму в бд
                # Получаем id номер созданного задания
                number_id = TaskModel.objects.get(task_number=new_post.task_number).id
                email_create_task(new_post, approved_user_list)
                # Добавляем файлы, если есть
                if request.FILES:
                    for f in request.FILES.getlist('file'):
                        obj = AttachmentFilesModel(file=f, task_id=number_id)
                        obj.save()
                if len(approved_user_list) > 0:
                    for app_user in approved_user_list:
                        obj = ApproveModel(approve_task_id=number_id, approve_user_id=app_user)
                        obj.save()
                if len(incoming_deps_list) == 1:
                    # Если отдел был всего 1, то перенаправляем на страницу с деталями задания, иначе перекидываем на страницу всех исходящих заданий
                    # number_id_for_redirect = TaskModel.objects.get(task_number=new_post.task_number).id
                    return redirect(f'/details/{number_id}')
        return redirect('my_tasks_on_sign')


class EditTaskView(View):
    """
    Страница редактирования записи.
    Реализация через UpdateView не возможна, так как в исходном class AddTask формируется номер нового задания,
    а нам необходимо обновить данные уже существующего
    """

    @method_decorator(login_required(login_url='login'))
    def get(self, request, pk):
        """Получаем номер редактируемого задания из query params (pk) и заполняем форму с данными из бд"""
        obj = TaskModel.objects.get(pk=pk)
        form = get_task_edit_form(request, obj)

        context = {
            'form': form,
            'user': Employee.objects.get(user=request.user),
            'obj': obj
        }
        return render(request, 'todo_tasks/add_task/update_task.html', context)

    def post(self, request, pk):
        """Обновляем данные базы данных"""
        if 'delete_number' in request.POST:
            print(pk, ' delete')
            return redirect(f'index')
        else:
            form = TaskEditForm(request.POST)
            # if form.is_valid():
            obj = TaskModel.objects.get(pk=pk)  # Получаем объект из бд
            # Присваиваем вручную новые данные из формы, почему только так работает, сказать не могу
            # Номер задания и автор остаются исходными
            obj.text_task = form.data['text_task']
            obj.first_sign_user_id = form.data['first_sign_user']
            obj.second_sign_user_id = form.data['second_sign_user']
            obj.incoming_dep_id = form.data['incoming_dep']
            obj.task_building = form.data['task_building']
            # На случай, если задание было возвращено, обнуляем значения подписей и флаг back_to_change
            obj.first_sign_status = 0
            obj.second_sign_status = 0
            obj.cpe_sign_status = 0
            obj.back_to_change = 0
            obj.task_last_edit = timezone.now()  # обновляем дату последнего изменения
            # Сохраняем новые данные в базу данных
            obj.save()
            #  Получаем список согласователей для аннулирования статуса
            approve_emp = ApproveModel.objects.get_queryset().filter(approve_task_id=pk)
            email_change_task(obj, approve_emp)
            for emp in approve_emp:
                # Аннулируем статус согласованности
                emp.approve_status = False
                emp.save()
            return redirect(f'/details/{pk}')


class EditTaskFiles(View):
    """Страница корректировки приложенных файлов"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request, pk):
        user = Employee.objects.get(user=request.user)  # "логинимся"
        obj = TaskModel.objects.get(id=pk)  # Получаем информацию по заданию
        file_form = FilesUploadForm()  # загружаем форму для отправки файлов
        old_files = AttachmentFilesModel.objects.get_queryset().filter(
            task_id=pk)  # Получаем список уже имеющихся файлов

        # Формируем список id этих объектов

        if user.cpe_flag is True:
            objects_queryset = CpeModel.objects.get_queryset().filter(cpe_user=user)
            list_objects = []
            for l_obj in objects_queryset:
                list_objects.append(l_obj.cpe_object_id)
                if obj.task_object in list_objects:
                    cpe_flag = True
                else:
                    cpe_flag = False
        else:
            cpe_flag = False

        content = {"file_form": file_form,
                   "old_files": old_files,
                   "user": user,
                   'obj': obj,
                   'cpe_flag': cpe_flag,
                   }
        return render(request, 'todo_tasks/files/change_files.html', content)

    def post(self, request, pk):
        """Загрузка новых файлов"""
        if request.FILES:
            for f in request.FILES.getlist('file'):
                obj = AttachmentFilesModel(file=f, task_id=pk)
                obj.save()
        old_files = AttachmentFilesModel.objects.get_queryset().filter(task_id=pk)
        obj = TaskModel.objects.get(pk=pk)
        obj.first_sign_status = False
        obj.second_sign_status = False
        obj.save()
        #  Получаем список согласователей
        approve_emp = ApproveModel.objects.get_queryset().filter(approve_task_id=pk)
        email_change_task(obj, approve_emp)
        for emp in approve_emp:
            # Аннулируем статус согласованности
            emp.approve_status = False
            emp.save()
        content = {"old_files": old_files}
        return render(request, 'todo_tasks/htmx/list_files.html', content)

    def delete(self, request, pk):
        print(pk)
        file = AttachmentFilesModel.objects.get(id=pk)
        task_id = file.task_id
        os.remove(os.path.join(settings.MEDIA_ROOT, str(file.file)))
        AttachmentFilesModel.objects.get(id=pk).delete()
        old_files = AttachmentFilesModel.objects.get_queryset().filter(task_id=task_id)

        print(old_files)
        content = {"old_files": old_files}
        return render(request, 'todo_tasks/htmx/list_files.html', content)


class AddChangeTaskView(View):
    """Выдать изменение к заданию"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request, pk):
        obj = TaskModel.objects.get(pk=pk)
        if obj.task_status == 1:
            return redirect('index')
        # заполняем форму данными из существующего задания
        form = get_task_edit_form(request, obj)

        context = {
            'form': form,
            'user': Employee.objects.get(user=request.user),
            'obj': obj}

        return render(request, 'todo_tasks/add_task/add_task_change.html', context)

    def post(self, request, pk):
        """Выдача изменения"""
        form = TaskEditForm(request.POST)
        changing_task = TaskModel.objects.get(pk=pk)  # Получаем данные существующего задания
        changing_task.task_status = 0  # аннулируем задание на которое выдается изменение
        changing_task.save()
        new_task_with_change = TaskModel(
            author=Employee.objects.get(user=request.user))  # Новое задание, автор пользователь из запроса
        # Берем старое изменение и увеличиваем
        new_task_with_change.task_change_number = changing_task.task_change_number + 1
        # Копируем данные со старого задания
        new_task_with_change.task_order = changing_task.task_order
        new_task_with_change.task_object = changing_task.task_object
        new_task_with_change.task_contract = changing_task.task_contract
        new_task_with_change.task_stage = changing_task.task_stage
        new_task_with_change.department_number = changing_task.department_number
        new_task_with_change.task_type_work = changing_task.task_type_work
        # Присваиваем номер задания с изменением
        task_name = str(changing_task.task_number).split('/')
        new_task_with_change.task_number = f'{task_name[0]}/И{new_task_with_change.task_change_number}'
        # Присваиваем данные из формы
        new_task_with_change.text_task = form.data['text_task']
        new_task_with_change.second_sign_user_id = form.data['second_sign_user']
        new_task_with_change.first_sign_user_id = form.data['first_sign_user']
        new_task_with_change.incoming_dep_id = form.data['incoming_dep']
        new_task_with_change.task_last_edit = timezone.now()

        new_task_with_change.save()
        # Получаем id выданного задания, для формирования ссылки
        number_id_for_redirect = TaskModel.objects.get(task_number=new_task_with_change.task_number).id
        return redirect(f'/details/{number_id_for_redirect}')


class MyInboxListView(View):
    """Получение моих входящих, где назначен исполнителем"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        user = Employee.objects.get(user=request.user)
        # Формируем 2 списка прочтенных и не прочтенных заданий
        tasks_id_unread = WorkerModel.objects.get_queryset().filter(worker_user=user).filter(read_status=False)
        tasks_id_read = WorkerModel.objects.get_queryset().filter(worker_user=user).filter(read_status=True)
        # Переводим в список
        task_list_unread = []
        for task in tasks_id_unread:
            task_list_unread.append(task.task_id)
        data_all_unread = TaskModel.objects.get_queryset().filter(id__in=task_list_unread)
        task_list_read = []
        for task in tasks_id_read:
            task_list_read.append(task.task_id)
        data_all_read = TaskModel.objects.get_queryset().filter(id__in=task_list_read)
        content = {
            'user': user,
            'data_all_unread': data_all_unread,
            'data_all_read': data_all_read
        }
        return render(request, 'todo_tasks/my_tasks/my_inbox_tasks.html', content)


class MyInboxReadTask(View):
    """Отметка задания как прочтенное"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request, pk):
        user = Employee.objects.get(user=request.user)
        task = WorkerModel.objects.get(worker_user=user.id, task_id=pk)
        task.read_status = True
        task.save()
        return redirect(f'/details/{pk}')


class ToSignListView(View):
    """Страница со списком заданий ожидающих подписи для выдачи в другой отдел (исходящих)"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        sign_user = Employee.objects.get(user=request.user)  # получаем пользователя
        # получаем список заданий
        if sign_user.cpe_flag == True:
            sign_list_1 = get_list_to_sign_cpe(sign_user)
            sign_list_2 = get_list_to_sign(sign_user)
            sign_list__1 = [i for i in sign_list_1]
            sign_list = sign_list__1 + sign_list_2

        else:
            sign_list = get_list_to_sign(sign_user)
        content = {
            'sign_list': sign_list,
            'user': sign_user}
        return render(request, 'todo_tasks/to_sign/outgoing_to_sign.html', content)


class ToSignDetailView(View):
    """Страница подписи задания"""

    @method_decorator(login_required)
    def get(self, request, pk):
        content = get_data_for_detail(request, pk)
        user = Employee.objects.get(user=request.user)
        if user.cpe_flag == True:
            list_objects = []
            for obj in CpeModel.objects.get_queryset().filter(cpe_user=user):
                list_objects.append(obj.cpe_object_id)
            print(list_objects)
            if content['obj'].task_object.id in list_objects:
                content['cpe_flag'] = True
        else:
            content['cpe_flag'] = False
        return render(request, 'todo_tasks/details/details_outgoing_to_sign.html', content)

    # Отработка кнопок подписи задания
    def post(self, request, pk):
        obj = TaskModel.objects.get(pk=pk)
        if 'sign1' in request.POST:
            print(pk, ' sign')
            obj.first_sign_status = True
            obj.first_sign_date = timezone.now()
            obj.save()
            check_and_send_to_cpe(pk)
        elif 'sign2' in request.POST:
            obj.second_sign_status = True
            obj.second_sign_date = timezone.now()
            obj.save()
            check_and_send_to_cpe(pk)
            print(pk, ' sign')
        elif 'sign3' in request.POST:
            obj.cpe_sign_status = True
            obj.cpe_sign_date = timezone.now()
            obj.cpe_sign_user = Employee.objects.get(user=request.user)
            obj.save()
            email_after_cpe_sign(pk)
            # check_and_send_to_cpe(pk) Здесь будем отправлять получателю
            print(pk, ' sign')
        elif 'cancel1' in request.POST:
            print(pk, ' cancel1')
            obj.first_sign_status = False
            obj.first_sign_date = None
            obj.save()
        elif 'cancel2' in request.POST:
            print(pk, ' cancel1')
            obj.second_sign_status = False
            obj.second_sign_date = None
            obj.save()
        elif 'cancel3' in request.POST:
            print(pk, ' cancel1')
            obj.cpe_sign_status = False
            obj.cpe_sign_date = None
            obj.task_status = 1
            obj.save()
        elif 'back_to_change' in request.POST:
            obj.back_to_change = True
            obj.save()
            print(pk, ' back to change')
            return redirect('incoming_to_sign')
        elif 'back_modal_button' in request.POST:
            print(request.POST.get('back_modal_text'))
            if request.POST.get("checkbox") == 'need_edit':
                print(request.POST.get("checkbox"))
                obj.back_to_change = True
                obj.save()
                email_not_sign(pk, request.POST.get('back_modal_text'), request.user, True)
            else:
                email_not_sign(pk, request.POST.get('back_modal_text'), request.user)
            # obj =
        elif 'comment_modal_button' in request.POST:
            obj.cpe_sign_status = True
            obj.cpe_sign_date = timezone.now()
            obj.cpe_sign_user = Employee.objects.get(user=request.user)
            obj.cpe_comment = request.POST.get('comment_modal_text')
            obj.save()
            email_after_cpe_sign(pk)
            # check_and_send_to_cpe(pk) Здесь будем напрявлять исполнителю
            print(pk, request.POST.get('comment_modal_text'))
        return redirect(request.META['HTTP_REFERER'])


class IncomingListView(View):
    """Получение заданий на подпись согласно таблице CanAccept"""

    @method_decorator(login_required)
    def get(self, request):
        sign_user = Employee.objects.get(user=request.user)  # получаем пользователя
        tasks = get_list_incoming_tasks_to_sign(sign_user)
        # получаем список входящих заданий
        if sign_user.cpe_flag == True:
            sign_list = get_list_to_sign_cpe(sign_user)
        else:
            sign_list = get_list_to_sign(sign_user)
        content = {
            'tasks': tasks,
            'user': sign_user}
        return render(request, 'todo_tasks/to_sign/incoming_to_sign.html', content)


class IncomingSignDetails(View):
    """Просмотр деталей при подписании задания получающим"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request, pk):
        content = get_data_for_detail(request, pk)
        sign_user = Employee.objects.get(user=request.user)
        queryset = CanAcceptModel.objects.get_queryset().filter(user_accept=sign_user)
        list_departments = []
        for dep in queryset:
            list_departments.append(dep.dep_accept_id)
        if sign_user.department_id in list_departments:
            content['can_sign'] = True
        else:
            content['can_sign'] = False
            # content['cpe_flag'] = False
        return render(request, 'todo_tasks/details/details_to_incoming_sign.html', content)

    def post(self, request, pk):
        print(request)
        obj = TaskModel.objects.get(pk=pk)
        if 'sign_incoming' in request.POST:
            # Принимающий подписал
            user = Employee.objects.get(user=request.user)  # Логинимся
            obj.incoming_employee = user  # Присваиваем пользователя, который подписал
            obj.incoming_date = timezone.now()
            obj.incoming_status = True  # Статус подписания
            obj.task_status = 2  # Статус задания "Актуально"
            obj.save()
            incoming_sign_email(obj, user)
            return redirect('details_to_add_workers', pk=pk)  # редирект на страницу добавления работников
        elif 'not_incoming_button' in request.POST:
            #  Если отказался подписывать
            if request.POST.get("checkbox") == 'need_edit':
                # Если есть галочка, то ставим статус требует редактирования
                incoming_not_sign_email(pk, Employee.objects.get(user=request.user),
                                        request.POST.get("comment_modal_text"), True)
                obj.back_to_change = True
                obj.save()
            else:
                incoming_not_sign_email(pk, Employee.objects.get(user=request.user),
                                        request.POST.get("comment_modal_text"), False)
            return redirect('incoming_to_sign')


class ToWorkerListView(View):
    """Страница со списком заданий ожидающих назначить исполнителей"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        sign_user = Employee.objects.get(user=request.user)  # получаем пользователя
        tasks = get_list_incoming_tasks_to_workers(sign_user)  # Получаем queryset с заданиями
        print(tasks)
        content = {
            'data_without_workers': tasks,
            'user': sign_user}
        return render(request, 'todo_tasks/to_sign/incoming_to_workers.html', content)


class ToAddWorkersDetailView(View):
    """Подробная страница задания с возможностью добавления ответственных"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request, pk):
        sign_user = Employee.objects.get(user=request.user)
        content = get_data_for_detail(request, pk)
        formset = WorkerForm()
        formset.fields['worker_user'].queryset = Employee.objects.filter(department=sign_user.department)
        content['data_all'] = WorkerModel.objects.get_queryset().filter(task=pk)
        content["formset"] = formset
        return render(request, 'todo_tasks/workers/details_to_add_workers.html', content)

    def post(self, request, pk):
        worker_user = request.POST.get("worker_user")
        # При каждом новом добавлении пользователя обновляем статус задания (назначены исполнители)
        save_to_worker_list(request, pk)
        # Обновляем список исполнителей к данному заданию
        data_all = WorkerModel.objects.get_queryset().filter(task_id=pk)
        content = {"data_all": data_all}
        return render(request, 'todo_tasks/htmx/workers.html', content)

    def delete(self, request, pk):
        pk2 = WorkerModel.objects.get(id=pk).task_id
        delete_worker_email(pk)
        WorkerModel.objects.get(id=pk).delete()
        data_all = WorkerModel.objects.get_queryset().filter(task_id=pk2)
        content = {"data_all": data_all}
        print(content)
        return render(request, 'todo_tasks/htmx/workers.html', content)


class EditWorkerListView(View):
    """Получение страницы с пользователями ответственными по заданию"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        print("эта вьюха")
        """Метод загружает Select поле выбора принятых заданий """
        user = Employee.objects.get(user=request.user)  # "логинимся"
        form = WorkersEditForm()  # загружаем форму с заданиями
        # Фильтруем список по параметру: в каких отделах имеет право подписи
        form.fields["task"].queryset = get_list_to_change_workers(user)

        content = {"form": form,
                   "user": user,
                   }
        return render(request, 'todo_tasks/workers/edit_workers.html', content)

    def post(self, request):
        """
        POST запрос, получающий из формы номер задания и формирующий данные
        для подгрузки их на странице
        """
        user = Employee.objects.get(user=request.user)  # данные пользователя
        form = WorkersEditForm(request.POST)  # загружаем из формы
        task = form.data['task']  # Получаем
        data_all = WorkerModel.objects.get_queryset().filter(task_id=task)  # Получаем список по данному заданию
        formset = WorkerForm()  # получаем форму сотрудников
        # Фильтруем сотрудников своего отдела todo на сотрудников управления
        sign_user_departments = CanAcceptModel.objects.get_queryset().filter(user_accept=user)
        sign_user_departments_list = [obj.dep_accept for obj in sign_user_departments]
        formset.fields['worker_user'].queryset = Employee.objects.filter(department__in=sign_user_departments_list)
        content = {"data_all": data_all,
                   "task": task,
                   'formset': formset}
        return render(request, 'todo_tasks/htmx/edit_workers.html', content)


class EditWorkersDetailView(View):
    """View для обработки POST и DELETE запросов добавления/удаления сотрудников
    на странице редактирования ответственных """

    @method_decorator(login_required(login_url='login'))
    def get(self, request, pk):
        user = Employee.objects.get(user=request.user)
        obj = TaskModel.objects.get(id=pk)
        data_all = WorkerModel.objects.get_queryset().filter(task_id=pk)
        formset = WorkerForm()
        sign_user_departments = CanAcceptModel.objects.get_queryset().filter(user_accept=user)
        sign_user_departments_list = [obj.dep_accept for obj in sign_user_departments]
        formset.fields['worker_user'].queryset = Employee.objects.filter(department__in=sign_user_departments_list)
        content = {"data_all": data_all,
                   'user': user,
                   "obj": obj,
                   'formset': formset}
        return render(request, 'todo_tasks/workers/from_detail_to_change_workers.html', content)

    def post(self, request, pk):
        """ pk - id необходимого задания"""
        user = Employee.objects.get(user=request.user)
        print(pk, user)
        # При каждом новом добавлении пользователя обновляем статус задания (назначены исполнители)
        save_to_worker_list(request, pk)  # отправляем пользователя и pk в функцию сохраняющую значения в WorkersModel

        formset = WorkerForm()
        sign_user_departments = CanAcceptModel.objects.get_queryset().filter(user_accept=user)
        sign_user_departments_list = [obj.dep_accept for obj in sign_user_departments]
        formset.fields['worker_user'].queryset = Employee.objects.filter(department__in=sign_user_departments_list)
        # Обновляем список исполнителей к данному заданию
        data_all = WorkerModel.objects.get_queryset().filter(task_id=pk)
        content = {"data_all": data_all,
                   "task": pk,
                   "formset": formset
                   }
        return render(request, 'todo_tasks/htmx/edit_workers.html', content)

    def delete(self, request, pk):
        """pk - номер записи в таблице WorkersModel"""
        # Получаем id задания, для дальнейшего формирования списка исполнителей
        pk2 = WorkerModel.objects.get(id=pk).task_id
        WorkerModel.objects.get(id=pk).delete()
        data_all = WorkerModel.objects.get_queryset().filter(task_id=pk2)
        content = {"data_all": data_all}
        print(content)
        return render(request, 'todo_tasks/htmx/edit_workers.html', content)


class ApproveListView(View):
    """Страница со списком заданий ожидающих назначить исполнителей"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        sign_user = Employee.objects.get(user=request.user)  # получаем пользователя
        tasks = ApproveModel.objects.get_queryset().filter(approve_user_id=sign_user.id).filter(
            approve_status=False)  # Получаем queryset с заданиями
        tasks_list = []
        for task in tasks:
            tasks_list.append(task.approve_task_id)
        data_to_approve_sign = TaskModel.objects.get_queryset().filter(id__in=tasks_list)
        print(tasks)
        content = {
            'tasks': data_to_approve_sign,
            'user': sign_user}
        return render(request, 'todo_tasks/to_approve/approve_to_sign.html', content)


class ApproveDetailView(View):
    """Подпись согласователя"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request, pk):
        sign_user = Employee.objects.get(user=request.user)  # получаем пользователя
        content = get_data_for_detail(request, pk)
        if len(ApproveModel.objects.get_queryset().filter(approve_task_id=pk).filter(
                approve_user_id=sign_user.id).filter(approve_status=False)) == 1:
            content['approve_flag'] = True
        else:
            content['approve_flag'] = False
        return render(request, 'todo_tasks/details/details_to_approve.html', content)

    def post(self, request, pk):
        if 'approve_sign' in request.POST:
            sign_user = Employee.objects.get(user=request.user)
            obj_approve_model = ApproveModel.objects.get(approve_task_id=pk, approve_user_id=sign_user.id)
            obj_approve_model.approve_status = True
            obj_approve_model.approve_date = datetime.datetime.now()
            obj_approve_model.save()
            # Проверка, если все согласователи подписали, то ставим в таблице TaskModel task_approved = True
            if ApproveModel.objects.get_queryset().filter(
                    approve_task_id=pk).count() == ApproveModel.objects.get_queryset().filter(
                approve_task_id=pk).filter(approve_status=True).count():
                obj_task = TaskModel.objects.get(id=pk)
                obj_task.task_approved = True
                obj_task.save()
                check_and_send_to_cpe(pk)
        if 'modal_text' in request.POST:
            approve_give_comment_email(pk, request.user, request.POST.get('modal_text'))
        return redirect(request.META['HTTP_REFERER'])


class SearchView(View):
    """Отображение результатов поиска c главной страницы"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request, pk):
        """pk - строка, по которой происходит поиск"""
        user = Employee.objects.get(user=request.user)
        search_result = TaskModel.objects.filter(
            Q(text_task__icontains=pk) | Q(task_number__icontains=pk) | Q(author__last_name__icontains=pk) | Q(
                task_building__icontains=pk))
        content = {"search_result": search_result,
                   "search_word": pk,
                   "user": user}
        return render(request, 'todo_tasks/search/search_result.html', content)


class AdvancedSearchView(View):
    """Подробный поиск"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        queryset = TaskModel.objects
        user = Employee.objects.get(user=request.user)

        search_object = request.GET.get('task_object')
        search_building = request.GET.get('task_building')
        search_contract = request.GET.get('task_contract')
        search_stage = request.GET.get('task_stage')
        search_dep = request.GET.get('task_dep')
        search_incoming_dep = request.GET.get('task_incoming_dep')
        search_type_work = request.GET.get('type_work')
        search_date_start = request.GET.get('date_start')
        search_date_end = request.GET.get('date_end')
        search_task_text = request.GET.get('task_text')
        search_task_status = request.GET.get('task_status')
        data = {"task_object": search_object,
                "task_building": search_building,
                'task_contract': search_contract,
                'task_stage': search_stage,
                'task_dep': search_dep,
                'task_incoming_dep': search_incoming_dep,
                'type_work': search_type_work,
                'date_start': search_date_start,
                'date_end': search_date_end,
                "task_text": search_task_text,
                "task_status": search_task_status
                }
        if is_valid_queryparam(search_object):
            queryset = queryset.filter(task_object=search_object)
        if is_valid_queryparam(search_contract):
            queryset = queryset.filter(task_contract=search_contract)
        if is_valid_queryparam(search_stage):
            queryset = queryset.filter(task_stage=search_stage)
        if is_valid_queryparam(search_building):
            queryset = queryset.filter(task_building__icontains=search_building)
        if is_valid_queryparam(search_dep):
            queryset = queryset.filter(department_number=search_dep)
        if is_valid_queryparam(search_task_status):
            queryset = queryset.filter(task_status=search_task_status)
        if is_valid_queryparam(search_incoming_dep):
            queryset = queryset.filter(incoming_dep=search_incoming_dep)
        if is_valid_queryparam(search_type_work) and search_type_work != '0':
            queryset = queryset.filter(task_type_work=search_type_work)
        if is_valid_queryparam(search_date_start):
            queryset = queryset.filter(cpe_sign_date__gte=search_date_start)
        if is_valid_queryparam(search_date_end):
            queryset = queryset.filter(cpe_sign_date__lte=search_date_end)
        if is_valid_queryparam(search_task_text):
            queryset = queryset.filter(text_task__icontains=search_task_text)

        # Для того что бы можно было попасть с главной страницы, иначе падает в ошибку по типу объекта
        if hasattr(queryset, '__iter__') is False:
            queryset = TaskModel.objects.none()

        form = SearchForm(initial=data)
        content = {"user": user,
                   "form": form,
                   "search_result": queryset}
        return render(request, 'todo_tasks/search/advanced_search.html', content)


# class TestView(View):
#     def get(self, request):
#         user = Employee.objects.get(user=request.user)
#
#         content = {'user': user}
#         print(type(request.user))
#         # print(vars(request))
#
#         return render(request, 'todo_tasks/test_cancel.html', content)


#
#     def post(self, request):
#         worker_user = request.POST.get("form-0-worker_user")
#         obj = WorkerModel()
#         obj.task_id = 28
#         obj.read_status = False
#         obj.worker_user_id = request.POST.get("form-0-worker_user")
#         obj.save()
#         print(worker_user)
#         data_all = WorkerModel.objects.get_queryset()
#         content = {"data_all": data_all}
#         return render(request, 'todo_tasks/htmx/workers.html', content)

class EditApproveUserView(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request, pk):
        user = Employee.objects.get(user=request.user)
        obj = TaskModel.objects.get(id=pk)
        form = ApproveEditForm()
        old_approve = ApproveModel.objects.get_queryset().filter(approve_task_id=pk)
        content = {'user': user,
                   'old_approve': old_approve,
                   'obj': obj,
                   'form': form}
        return render(request, 'todo_tasks/approve_user/change_approve_user.html', content)

    def post(self, request, pk):
        print(request.POST.get('approve_user'))
        new_approve_emp = ApproveModel()
        new_approve_emp.approve_user_id = int(request.POST.get('approve_user'))
        new_approve_emp.approve_task_id = pk
        new_approve_emp.save()
        email_add_approver(pk, int(request.POST.get('approve_user')))
        old_approve = ApproveModel.objects.get_queryset().filter(approve_task_id=pk)
        content = {
            'old_approve': old_approve,
        }
        return render(request, 'todo_tasks/htmx/list_approve.html', content)

    def delete(self, request, pk):
        print(pk)
        pk2 = ApproveModel.objects.get(id=pk).approve_task_id
        approve_id = ApproveModel.objects.get(id=pk)
        approve_id.delete()
        old_approve = ApproveModel.objects.get_queryset().filter(approve_task_id=pk2)
        content = {
            'old_approve': old_approve,
        }
        return render(request, 'todo_tasks/htmx/list_approve.html', content)


class ObjectTasksListView(View):
    "Получение списка по объектам ГИП-а"

    def get(self, request):
        pass


# Функции AJAX

def load_contracts(request):
    """Функция для получения списка контрактов"""
    print("ajax load contracts пришел")  # Проверка, сработал ли ajax с отправкой данных
    object_id = request.GET.get("object")  # достаем значение объекта из запроса
    contracts = ContractModel.objects.filter(
        contract_object=int(object_id))  # получаем все контракты для данного объекта
    return render(request, 'todo_tasks/dropdown_update/contracts_dropdown_list_update.html', {'contracts': contracts})


def load_stages(request):
    """Функция для получения списка этапов"""
    print("ajax load stages пришел")  # Проверка, сработал ли ajax с отправкой данных
    contract_id = request.GET.get("contract")
    stages = StageModel.objects.filter(stage_contract=int(contract_id))
    return render(request, 'todo_tasks/dropdown_update/stages_dropdown_list_update.html', {'stages': stages})


def load_incoming_employee(request):
    """Функция для получения списка этапов"""
    print("ajax load employee пришел")  # Проверка, сработал ли ajax с отправкой данных
    department_id = request.GET.get("departament")
    incoming_employee = CanAcceptModel.objects.filter(user_accept__department_id=department_id)
    print(incoming_employee)
    return render(request, 'todo_tasks/dropdown_update/incoming_dropdown_list_update.html',
                  {'incoming_employee': incoming_employee})


class DownloadFileView(View):
    def get(self, request, pk):
        file_path_in_db = AttachmentFilesModel.objects.get(id=pk)
        # print(file_path_in_db.file)
        file_path = os.path.join(settings.MEDIA_ROOT, str(file_path_in_db.file))
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                mime_type, _ = mimetypes.guess_type(file_path)
                response = HttpResponse(fh.read(), content_type=mime_type)
                response['Content-Disposition'] = 'inline; filename=' + escape_uri_path(os.path.basename(file_path))
                return response
        raise Http404


class DownloadBlankView(View):
    @method_decorator(login_required(login_url='login'))
    def get(self, request, pk):
        pdf_gen(pk)
        task_inf = TaskModel.objects.get(id=pk)
        if os.path.exists(os.path.join(settings.BASE_DIR, 'media', 'files', str(task_inf.task_number))):
            with open(os.path.join(settings.BASE_DIR, 'media', 'files', str(task_inf.task_number),
                                   f'{task_inf.task_number}.pdf'), 'rb') as fh:
                mime_type, _ = mimetypes.guess_type(
                    os.path.join(settings.BASE_DIR, 'media', 'files', str(task_inf.task_number),
                                 f'{task_inf.task_number}.pdf'))
                response = HttpResponse(fh.read(), content_type=mime_type)
                response['Content-Disposition'] = "inline; filename=" + escape_uri_path(f'{task_inf.task_number}.pdf')
                return response
        raise Http404


class UserProfileView(View):
    """Страница просмотра профиля"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        user = Employee.objects.get(user=request.user)
        form = UserProfileForm(instance=user)
        content = {'form': form,
                   "user": user}
        return render(request, 'todo_tasks/system_user/user_profile.html', content)


class EditProfileUserView(View):
    """Страница редактирования профиля"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        try:
            user = Employee.objects.get(user=request.user)
            form = UserProfileForm(instance=user)
        except:
            form = UserProfileForm()
        content = {'form': form,
                   "user": request.user}
        return render(request, 'todo_tasks/system_user/edit_user_profile.html', content)

    def post(self, request):
        form = UserProfileForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.user = User.objects.get(username=request.user)
            try:
                employee.id = Employee.objects.get(user=request.user).id
            finally:
                employee.save()
        return redirect('profile')
