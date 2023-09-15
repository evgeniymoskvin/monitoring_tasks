import datetime
import mimetypes
import os.path
import copy

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
from django.contrib.auth import authenticate, login

from .models import Employee, TaskModel, ContractModel, ObjectModel, StageModel, TaskNumbersModel, CommandNumberModel, \
    CpeModel, CanAcceptModel, WorkerModel, ApproveModel, AttachmentFilesModel, FavoritesListModel, \
    TasksInFavoritesModel, FavoritesShareModel, CanChangeWorkersModel, DraftTaskModel
from .forms import TaskForm, TaskEditForm, SearchForm, WorkerForm, WorkersEditForm, \
    TaskFormForSave, ApproveForm, FilesUploadForm, UserProfileForm, ApproveEditForm, LoginForm, CreateFavoriteListForm, \
    ShareFavoriteListForm, AddMyFavoriteForm, AddShareFavoriteForm, SaveDraftForm
from .functions import get_data_for_detail, get_list_to_sign, get_task_edit_form, \
    get_list_to_sign_cpe, get_list_incoming_tasks_to_sign, get_list_incoming_tasks_to_workers, save_to_worker_list, \
    get_list_to_change_workers, is_valid_queryparam, get_can_change_favorites_access
from .pdf_making import pdf_gen
from .email_functions import email_create_task, check_and_send_to_cpe, email_after_cpe_sign, delete_worker_email, \
    incoming_not_sign_email, email_not_sign, email_change_task, approve_give_comment_email, email_add_approver, \
    incoming_sign_email


class AboutView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('index')
        form_login = LoginForm()
        content = {
            "login_form": form_login,
        }
        return render(request, 'todo_tasks/about.html', content)

    def post(self, request):
        if User.objects.filter(username=request.POST['username']).exists():
            user = authenticate(username=request.POST['username'], password=request.POST['password'])
            try:
                login(request, user)
                return redirect('index')
            except:
                return redirect('login')
        else:
            return redirect('login')
        return redirect('about')

        # form_login = LoginForm(request.POST)
        # print(form_login)
        # content = {
        #     "login_form": form_login,
        # }


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
        data_to_sign = TaskModel.objects.get_queryset().filter(department_number=user.department).filter(
            task_status=1).order_by('-id')
        content = {'data_to_sign': data_to_sign,
                   'user': user}
        return render(request, 'todo_tasks/department_tasks/outgoing_tasks.html', content)


class IncomingDepView(View):
    """Страница входящих заданий по номеру отделу пользователя"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        user = Employee.objects.get(user=request.user)  # Получаем пользователя из запроса
        user_dep = user.department_id  # получаем id номер отдела
        data_have_workers = TaskModel.objects.get_queryset().filter(incoming_dep=user_dep).filter(
            task_status=2).order_by('-id')
        content = {'data_have_workers': data_have_workers,
                   'user': user}
        return render(request, 'todo_tasks/department_tasks/incoming_to_dep.html', content)


class UserTaskView(View):
    """Просмотр "мои выданные" заданий """

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        data_user = TaskModel.objects.get_queryset().filter(author__user=request.user).filter(task_status=2).order_by(
            '-id')
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
        data_user = TaskModel.objects.get_queryset().filter(author__user=request.user).filter(task_status=1).order_by(
            '-id')
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
        if CanChangeWorkersModel.objects.get_queryset().filter(user_accept=content['user']):
            content['change_work_flag'] = True
        content[
            'flag'] = True  # Для того, что бы шестеренка была доступна только на странице деталей, и ни на каких других дочерних
        to_my_favorite_form = AddMyFavoriteForm()
        to_share_favorite_form = AddShareFavoriteForm()
        # Получаем список чужих избранных в которые можем вносить изменения
        sharing_favorite_list = FavoritesShareModel.objects.get_queryset().filter(
            favorite_share_user_id=content['user']).filter(can_change_list=True)
        list_sharing_favorites = [i.favorite_list.id for i in sharing_favorite_list]
        sharing_favorite_list_to_form = FavoritesListModel.objects.filter(id__in=list_sharing_favorites)
        # Получаем список своих избранных и добавляем к ним чужие
        to_my_favorite_form.fields['favorite_list'].queryset = FavoritesListModel.objects.filter(
            favorite_list_holder=content['user']).union(sharing_favorite_list_to_form)
        content['to_my_favorite_form'] = to_my_favorite_form
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
        approve_form.fields['approve_user'].queryset = Employee.objects.filter(cpe_flag=False).filter(
            work_status=True).order_by("last_name")
        # Фильтруем поля руководителей в соответствии с отделом пользователя
        department_user = Employee.objects.get(user=request.user).department  # получаем номер отдела
        form.fields['first_sign_user'].queryset = Employee.objects.filter(department=department_user).filter(
            right_to_sign=True)  # получаем в 1ое поле список пользователей по двум фильтрам
        form.fields['second_sign_user'].queryset = Employee.objects.filter(department=department_user).filter(
            right_to_sign=True)  # получаем во 2ое поле список пользователей по двум фильтрам
        file_form = FilesUploadForm()
        draft_form = SaveDraftForm()
        objects = ObjectModel.objects.all()
        draft_contract_flag = 0
        draft_stage_flag = 0
        draft_object_flag = 0
        context = {'form': form,
                   "file_form": file_form,
                   "draft_form": draft_form,
                   'user': Employee.objects.get(user=request.user),
                   'objects': objects,
                   "approve_form": approve_form,
                   "draft_contract_flag": draft_contract_flag,
                   "draft_stage_flag": draft_stage_flag,
                   "draft_object_flag": draft_object_flag,
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
            try:
                value_contract = temp_req['task_contract']
                if temp_req['task_contract'] == '0':
                    temp_req['task_contract'] = ''
            except:
                temp_req['task_contract'] = ''

            try:
                value_stage = temp_req['task_stage']
                if value_stage == '0':
                    temp_req['task_stage'] = ''
            except:
                temp_req['task_stage'] = ''
            # Грузим в форму для сохранения
            form = TaskFormForSave(temp_req)
            # print(form.data)
            # if form.task_stage:
            #     print('asd')

            if form.is_valid():
                new_post = form.save(commit=False)  # отменяем отправку form в базу
                new_post.department_number = CommandNumberModel.objects.get(id=dep)  # Присваиваем отдел
                new_post.author = Employee.objects.get(user=request.user)  # добавляем пользователя из request
                new_post.department_number = new_post.author.department  # добавляем номер отдела пользователя, пока не знаю зачем
                # Получаем номер последнего задания из таблицы TaskNumbers
                try:
                    last_number = TaskNumbersModel.objects.get(command_number=new_post.department_number)
                except:
                    TaskNumbersModel.objects.create(command_number=new_post.department_number, count_of_task=0).save()
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
                elif len(approved_user_list) == 0 and new_post.task_need_approve is True:
                    new_post.task_need_approve = False
                    new_post.task_approved = True
                new_post.task_last_edit = datetime.datetime.now()  # Присваиваем дату последнего изменения

                new_post.task_number = f'ЗД-{new_post.department_number.command_number}-{last_number.count_of_task}-{str(today_year)[2:4]}'
                new_post.task_change_number = 0  # номер изменения присваиваем 0
                # print(new_post.task_order)
                # print(new_post.task_number)
                form.save()  # сохраняем форму в бд
                # Получаем id номер созданного задания
                number_id = TaskModel.objects.get(task_number=new_post.task_number).id
                email_create_task(new_post, approved_user_list)
                # Добавляем файлы, если есть
                if request.FILES:
                    list_copy_files = copy.deepcopy(request.FILES.getlist('file'))
                    for f in list_copy_files:
                        obj = AttachmentFilesModel(file=f, task_id=number_id)
                        obj.save()
                    del list_copy_files
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
            obj = TaskModel.objects.get(pk=pk)
            obj.delete()
            print(pk, ' delete')
            return redirect(f'my_tasks_on_sign')
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
        file = AttachmentFilesModel.objects.get(id=pk)
        task_id = file.task_id
        os.remove(os.path.join(settings.MEDIA_ROOT, str(file.file)))
        AttachmentFilesModel.objects.get(id=pk).delete()
        #  Получаем список согласователей
        approve_emp = ApproveModel.objects.get_queryset().filter(approve_task_id=task_id)
        obj = TaskModel.objects.get(pk=task_id)
        email_change_task(obj, approve_emp)
        for emp in approve_emp:
            # Аннулируем статус согласованности
            emp.approve_status = False
            emp.save()
        old_files = AttachmentFilesModel.objects.get_queryset().filter(task_id=task_id)
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
        new_task_with_change.task_building = changing_task.task_building
        new_task_with_change.task_object = changing_task.task_object
        new_task_with_change.task_mark_doc = changing_task.task_mark_doc
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
        tasks_id_unread = WorkerModel.objects.get_queryset().filter(worker_user=user).filter(
            read_status=False).order_by('-id')
        tasks_id_read = WorkerModel.objects.get_queryset().filter(worker_user=user).filter(read_status=True).order_by(
            '-id')
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
            if content['obj'].task_object.id in list_objects:
                content['cpe_flag'] = True
        else:
            content['cpe_flag'] = False
            content['flag'] = True
        return render(request, 'todo_tasks/details/details_outgoing_to_sign.html', content)

    # Отработка кнопок подписи задания
    def post(self, request, pk):
        obj = TaskModel.objects.get(pk=pk)
        if 'sign1' in request.POST:
            print(pk, ' sign', obj)
            obj.first_sign_status = True
            obj.first_sign_date = timezone.now()
            obj.save()
            check_and_send_to_cpe(pk)
        elif 'sign2' in request.POST:
            obj.second_sign_status = True
            obj.second_sign_date = timezone.now()
            obj.save()
            check_and_send_to_cpe(pk)
            print(pk, ' sign', obj)
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
            list_departments.append(dep.dep_accept)
            print(dep.dep_accept)
        if content['obj'].incoming_dep in list_departments:
            content['can_sign'] = True
        # elif sign_user.department_id in list_departments:
        #     content['can_sign'] = True
        else:
            content['can_sign'] = False

        return render(request, 'todo_tasks/details/details_to_incoming_sign.html', content)

    def post(self, request, pk):
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
        formset.fields['worker_user'].queryset = Employee.objects.filter(
            department_group=sign_user.department_group).filter(work_status=True)
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
        return render(request, 'todo_tasks/htmx/workers.html', content)


class EditWorkerListView(View):
    """Получение страницы с пользователями ответственными по заданию"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
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
        if len(sign_user_departments_list) > 0:
            formset.fields['worker_user'].queryset = Employee.objects.filter(
                department__in=sign_user_departments_list).filter(work_status=True)
        elif CanChangeWorkersModel.objects.get_queryset().filter(user_accept=user).count() > 0:
            formset.fields['worker_user'].queryset = Employee.objects.filter(department=user.department)
        content = {"data_all": data_all,
                   'user': user,
                   "obj": obj,
                   'formset': formset}
        return render(request, 'todo_tasks/workers/from_detail_to_change_workers.html', content)

    def post(self, request, pk):
        """ pk - id необходимого задания"""
        user = Employee.objects.get(user=request.user)
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
        return render(request, 'todo_tasks/htmx/edit_workers.html', content)


class ApproveListView(View):
    """Страница со списком заданий ожидающих назначить исполнителей"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        sign_user = Employee.objects.get(user=request.user)  # получаем пользователя
        tasks = ApproveModel.objects.get_queryset().filter(approve_user_id=sign_user.id).filter(
            approve_status=False).order_by('-id')  # Получаем queryset с заданиями
        tasks_list = []
        for task in tasks:
            tasks_list.append(task.approve_task_id)
        data_to_approve_sign = TaskModel.objects.get_queryset().filter(id__in=tasks_list)
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


class DeleteApproveSelf(View):
    """Удаление самого себе из списка согласователей"""

    def get(self, request, pk):
        user = Employee.objects.get(user=request.user)
        obj = ApproveModel.objects.filter(approve_task_id=pk).filter(approve_user=user)
        obj.delete()
        print(pk)
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
        search_status = False

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
            search_status = True

        form = SearchForm(initial=data)
        content = {"user": user,
                   "form": form,
                   "search_result": queryset,
                   "search_status": search_status}
        return render(request, 'todo_tasks/search/advanced_search.html', content)


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
        status_approve_emp = ApproveModel.objects.get_queryset().filter(approve_task_id=pk).filter(
            approve_user_id=int(request.POST.get('approve_user'))).exists()
        if status_approve_emp:
            print("Такой пользователь уже добавлен в согласователи")
        else:
            new_approve_emp.approve_task_id = pk
            new_approve_emp.save()
            print(new_approve_emp)
            email_add_approver(pk, int(request.POST.get('approve_user')))
        old_approve = ApproveModel.objects.get_queryset().filter(approve_task_id=pk)
        content = {
            'old_approve': old_approve,
        }
        return render(request, 'todo_tasks/htmx/list_approve.html', content)

    def delete(self, request, pk):
        pk2 = ApproveModel.objects.get(id=pk).approve_task_id
        approve_id = ApproveModel.objects.get(id=pk)
        approve_id.delete()
        old_approve = ApproveModel.objects.get_queryset().filter(approve_task_id=pk2)
        content = {
            'old_approve': old_approve,
        }
        return render(request, 'todo_tasks/htmx/list_approve.html', content)


class RedirectApproveUserView(View):
    """Добавление сотрудников для согласования самим согласователем"""

    def post(self, request, pk):
        new_approve_emp = ApproveModel()
        new_approve_emp.approve_user_id = int(request.POST.get('approve_user'))
        status_approve_emp = ApproveModel.objects.get_queryset().filter(approve_task_id=pk).filter(
            approve_user_id=int(request.POST.get('approve_user'))).exists()
        if status_approve_emp:
            print("Такой пользователь уже добавлен в согласователи")
        else:
            new_approve_emp.approve_task_id = pk
            new_approve_emp.save()
            print(new_approve_emp)
            email_add_approver(pk, int(request.POST.get('approve_user')))

        return redirect(request.META['HTTP_REFERER'])


class ObjectTasksListView(View):
    "Получение списка по объектам ГИП-а"

    def get(self, request):
        pass


# Функции AJAX

def load_contracts(request):
    """Функция для получения списка контрактов"""
    # print("ajax load contracts пришел")  # Проверка, сработал ли ajax с отправкой данных
    object_id = request.GET.get("object")  # достаем значение объекта из запроса
    contracts = ContractModel.objects.filter(
        contract_object=int(object_id)).filter(show=True)  # получаем все контракты для данного объекта
    return render(request, 'todo_tasks/dropdown_update/contracts_dropdown_list_update.html', {'contracts': contracts})


def load_stages(request):
    """Функция для получения списка этапов"""
    # print("ajax load stages пришел")  # Проверка, сработал ли ajax с отправкой данных
    contract_id = request.GET.get("contract")
    stages = StageModel.objects.filter(stage_contract=int(contract_id))
    return render(request, 'todo_tasks/dropdown_update/stages_dropdown_list_update.html', {'stages': stages})


def load_incoming_employee(request):
    """Функция для получения списка этапов"""
    # print("ajax load employee пришел")  # Проверка, сработал ли ajax с отправкой данных
    department_id = request.GET.get("departament")
    incoming_employee = CanAcceptModel.objects.filter(user_accept__department_id=department_id)
    # print(incoming_employee)
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
                   "user": user,
                   }
        return render(request, 'todo_tasks/system_user/user_profile.html', content)

    def post(self, request):
        """Включение/отключение рассылок"""
        user = Employee.objects.get(user=request.user)
        if request.POST.get('mailing_check') == 'on':
            user.mailing_list_check = True
            user.save()
        else:
            user.mailing_list_check = False
            user.save()
        return redirect('profile')


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
            employee_form = form.save(commit=False)
            check_user = Employee.objects.get_queryset().filter(user=request.user)
            if check_user:
                employee = Employee.objects.get(user=request.user)
                employee.last_name = employee_form.last_name
                employee.first_name = employee_form.first_name
                employee.last_name = employee_form.last_name
                employee.job_title = employee_form.job_title
                employee.department = employee.department
                employee.department_group = employee_form.department_group
                employee.user_phone = employee_form.user_phone
                employee.personnel_number = employee_form.personnel_number
                employee.work_status = True
                employee.save()
            else:
                employee_form.user_id = User.objects.get(username=request.user).id
                employee_form.save()
        employee = Employee.objects.get(user=request.user)
        employee.work_status = True
        employee.save()
        return redirect('profile')


class FavoritesListView(View):
    """Страница списков избранного пользователя"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        user = Employee.objects.get(user=request.user)
        list_favorites = FavoritesListModel.objects.get_queryset().filter(favorite_list_holder=user)
        share_list_favorites = FavoritesShareModel.objects.get_queryset().filter(favorite_share_user=user)
        form = CreateFavoriteListForm()
        content = {'list_favorites': list_favorites,
                   "user": user,
                   "form_create_list": form,
                   "share_list_favorites": share_list_favorites
                   }
        return render(request, 'todo_tasks/favorites/favorites_lists.html', content)

    def post(self, request):
        """post запрос создания нового списка"""
        form = CreateFavoriteListForm(request.POST)
        new_list_favorites = form.save(commit=False)
        new_list_favorites.favorite_list_holder = Employee.objects.get(user=request.user)
        new_list_favorites.save()
        return redirect(f'favorites')


class CurrentFavoritesListView(View):
    """Страница списков избранного пользователя"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request, pk):
        user = Employee.objects.get(user=request.user)
        list_name = FavoritesListModel.objects.get(id=pk)
        access_flag = False
        can_change_flag = False
        holder_flag = False
        data_all_favorites = TasksInFavoritesModel.objects.none()
        can_view_favorites = FavoritesShareModel.objects.get_queryset().filter(favorite_list_id=pk).filter(
            favorite_share_user=user)
        can_change_favorites = FavoritesShareModel.objects.get_queryset().filter(favorite_list_id=pk).filter(
            favorite_share_user=user).filter(can_change_list=True)

        # Получение флагов, для управления избранным
        if (list_name.favorite_list_holder == user) or (can_view_favorites):
            access_flag = True
            data_all_favorites = TasksInFavoritesModel.objects.get_queryset().filter(favorite_list_id=pk)

        if (list_name.favorite_list_holder == user):
            holder_flag = True

        if can_change_favorites:
            can_change_flag = True

        content = {
            "user": user,
            "list_name": list_name,
            "access_flag": access_flag,
            "data_all_favorites": data_all_favorites,
            "can_change_flag": can_change_flag,
            "holder_flag": holder_flag

        }
        return render(request, 'todo_tasks/favorites/current_favorites_list.html', content)


class ShareFavoritesListView(View):
    "Страница редактирования достпуа к избранному списку"

    @method_decorator(login_required(login_url='login'))
    def get(self, request, pk):
        user = Employee.objects.get(user=request.user)
        list_name = FavoritesListModel.objects.get(id=pk)
        share_form = ShareFavoriteListForm()
        share_users_list = FavoritesShareModel.objects.get_queryset().filter(favorite_list_id=pk)
        access_flag = get_can_change_favorites_access(pk, user, list_name)

        content = {
            "user": user,
            "access_flag": access_flag,
            "list_name": list_name,
            "share_form": share_form,
            "share_users_list": share_users_list

        }
        return render(request, 'todo_tasks/favorites/share_favorite_list.html', content)

    def post(self, request, pk):
        share_form = ShareFavoriteListForm(request.POST)
        if share_form.is_valid():
            new_share_user_favorites = share_form.save(commit=False)
            new_share_user_favorites.favorite_list = FavoritesListModel.objects.get(id=pk)
            # Проверяем, есть ли такой доступ, если есть, ничего не меняем
            if FavoritesShareModel.objects.filter(favorite_list_id=new_share_user_favorites.favorite_list).filter(
                    favorite_share_user=new_share_user_favorites.favorite_share_user):
                return redirect(request.META['HTTP_REFERER'])
            else:
                new_share_user_favorites.save()
                return redirect(request.META['HTTP_REFERER'])


class DeleteShareFavoritesListView(View):
    """Удаление доступа к списку"""

    def post(self, request, pk):
        delete_share = FavoritesShareModel.objects.get(id=pk)
        delete_share.delete()
        return redirect(request.META['HTTP_REFERER'])


class AddTaskFavoritesListView(View):
    """Добавление в избранное"""

    def post(self, request, pk):
        form = AddMyFavoriteForm(request.POST)
        if form.is_valid():
            new_share = form.save(commit=False)
            # Проверяем, есть ли задание в списке
            check_tasks = TasksInFavoritesModel.objects.filter(favorite_task_id=pk).filter(
                favorite_list_id=new_share.favorite_list_id)
            if check_tasks.count() == 0:
                new_share.favorite_task_id = pk
                new_share.save()
        return redirect(request.META['HTTP_REFERER'])


class EditFavoriteListView(View):
    """Редактирование списка в избранном"""

    def get(self, request, pk):
        user = Employee.objects.get(user=request.user)
        list_name = FavoritesListModel.objects.get(id=pk)
        favorites_tasks = TasksInFavoritesModel.objects.get_queryset().filter(favorite_list_id=pk)
        access_flag = get_can_change_favorites_access(pk, user, list_name)
        content = {
            "access_flag": access_flag,
            "user": user,
            "list_name": list_name,
            "favorites_tasks": favorites_tasks,
        }
        return render(request, 'todo_tasks/favorites/edit_current_favorite_list.html', content)

    def post(self, request, pk):
        """Удаление списка избранного"""
        FavoritesListModel.objects.get(id=pk).delete()
        return redirect('favorites')


class DeleteTaskFromFavoriteView(View):
    """Удаление избранного из списка"""

    def post(self, request, pk):
        task_to_delete = TasksInFavoritesModel.objects.get(id=pk)
        task_to_delete.delete()
        return redirect(request.META['HTTP_REFERER'])


def load_empolyee(request):
    """Фнкуия загрузки списка сотрудников"""
    approve_form = ApproveEditForm()
    content = {'approve_form': approve_form}
    return render(request, 'todo_tasks/ajax/load_list_employee.html', content)


def load_favorite_list(request):
    """Функция загрузки списка избранного"""
    user_id = int(request.GET.get("user_id"))
    to_my_favorite_form = AddMyFavoriteForm()
    # Получаем список чужих избранных в которые можем вносить изменения
    sharing_favorite_list = FavoritesShareModel.objects.get_queryset().filter(
        favorite_share_user_id=user_id).filter(can_change_list=True)
    list_sharing_favorites = [i.favorite_list.id for i in sharing_favorite_list]
    sharing_favorite_list_to_form = FavoritesListModel.objects.filter(id__in=list_sharing_favorites)
    # Получаем список своих избранных и добавляем к ним чужие
    to_my_favorite_form.fields['favorite_list'].queryset = FavoritesListModel.objects.filter(
        favorite_list_holder=user_id).union(sharing_favorite_list_to_form)
    content = {
        'to_my_favorite_form': to_my_favorite_form
    }
    return render(request, 'todo_tasks/ajax/load_favorite_list.html', content)


def save_draft(request):
    """Сохранение черновиков"""
    new_draft = DraftTaskModel()
    new_draft.author_id = int(request.GET.get("user_id"))
    if request.GET.get("id_text_task") != "NaN":
        new_draft.draft_text = str(request.GET.get("id_text_task"))
    if request.GET.get("id_task_building") != "NaN":
        new_draft.draft_building = str(request.GET.get("id_task_building"))
    if request.GET.get("id_draft_name") != "NaN":
        new_draft.draft_name = str(request.GET.get("id_draft_name"))

    # Проверка численных значений пришедших с фронтенда
    try:
        if int(request.GET.get("objectId")) > 0:
            new_draft.draft_object_id = int(request.GET.get("objectId"))
    except Exception as e:
        print(f'{e}, objectId {request.GET.get("objectId")}')
    try:
        if int(request.GET.get("id_task_contract")) > 0:
            new_draft.draft_contract_id = int(request.GET.get("id_task_contract"))
    except Exception as e:
        print(f'{e}, id_task_contract {request.GET.get("id_task_contract")}')

    try:
        if int(request.GET.get("id_task_type_work")):
            new_draft.draft_type_work = int(request.GET.get("id_task_type_work"))
    except Exception as e:
        print(f'{e}, id_task_type_work {request.GET.get("id_task_type_work")}')

    try:
        if int(request.GET.get("id_first_sign_user")) > 0:
            new_draft.first_sign_user_id = int(request.GET.get("id_first_sign_user"))
    except Exception as e:
        print(f'{e}, id_first_sign_user {request.GET.get("id_first_sign_user")}')

    try:
        if int(request.GET.get("id_second_sign_user")) > 0:
            new_draft.second_sign_user_id = int(request.GET.get("id_second_sign_user"))
    except Exception as e:
        print(f'{e}, id_second_sign_user {request.GET.get("id_second_sign_user")}')

    try:
        if int(request.GET.get("id_task_mark_doc")) > 0:
            new_draft.draft_mark_doc_id = int(request.GET.get("id_task_mark_doc"))
    except Exception as e:
        print(f'{e}, id_task_mark_doc {request.GET.get("id_task_mark_doc")}')

    try:
        if int(request.GET.get("id_task_stage")) > 0:
            new_draft.draft_stage_id = int(request.GET.get("id_task_stage"))
    except Exception as e:
        print(f'{e}, id_task_stage {request.GET.get("id_task_stage")}')
    new_draft.save()
    print(f'Черновик {new_draft} создан')
    return render(request, 'todo_tasks/ajax/save_draft_notification.html')


def load_drafts(request):
    """Загрузка списка черновиков пользователя"""
    user = int(request.GET.get("user_id"))
    obj = DraftTaskModel.objects.get_queryset().filter(author_id=user).order_by('-id')
    content = {
        'obj': obj,
    }
    return render(request, 'todo_tasks/ajax/load_drafts_list.html', content)


def load_current_draft(request):
    """Загрузка конктректного черновика"""
    draft_id = int(request.GET.get("draft_id"))
    draft = DraftTaskModel.objects.get(id=draft_id)
    form = TaskForm()  # Форма задания
    approve_form = ApproveForm()  # Форма согласователей
    approve_form.fields['approve_user'].queryset = Employee.objects.filter(cpe_flag=False).filter(
        work_status=True).order_by("last_name")
    # Фильтруем поля руководителей в соответствии с отделом пользователя
    department_user = Employee.objects.get(user=request.user).department  # получаем номер отдела
    form.fields['first_sign_user'].queryset = Employee.objects.filter(department=department_user).filter(
        right_to_sign=True)  # получаем в 1ое поле список пользователей по двум фильтрам
    form.fields['second_sign_user'].queryset = Employee.objects.filter(department=department_user).filter(
        right_to_sign=True)  # получаем во 2ое поле список пользователей по двум фильтрам
    form.fields['task_contract'].queryset = ContractModel.objects
    file_form = FilesUploadForm()
    objects = ObjectModel.objects.all()
    draft_object_flag = 0
    draft_contract_flag = 0
    draft_stage_flag = 0
    if draft.draft_contract:
        draft_contract_flag = draft.draft_contract_id
    if draft.draft_stage:
        draft_stage_flag = draft.draft_stage_id
    if draft.draft_object:
        draft_object_flag = draft.draft_object_id
    form = TaskForm(initial={'text_task': draft.draft_text,
                             'task_object': draft.draft_object_id,
                             'task_building': draft.draft_building,
                             'first_sign_user': draft.first_sign_user_id,
                             'second_sign_user': draft.second_sign_user_id,
                             'task_mark_doc': draft.draft_mark_doc_id,
                             'task_type_work': draft.draft_type_work,
                             'task_contract': draft.draft_contract_id,
                             "task_stage": draft.draft_stage_id})
    content = {'form': form,
               "file_form": file_form,
               'objects': objects,
               "approve_form": approve_form,
               "draft_contract_flag": draft_contract_flag,
               "draft_stage_flag": draft_stage_flag,
               "draft_object_flag": draft_object_flag,
               }
    return render(request, 'todo_tasks/add_task/add_form.html', content)


def delete_current_draft(request):
    """Удаление конкретного черновика"""
    delete_draft_id = int(request.GET.get("draft_id"))
    draft = DraftTaskModel.objects.get(id=delete_draft_id)
    print(f"Черновик {draft} удален")
    draft.delete()
    return HttpResponse('')


def delete_all_drafts(request):
    """Удаление всех черновиков"""
    user = int(request.GET.get("user_id"))
    drafts = DraftTaskModel.objects.get_queryset().filter(author_id=user)
    for draft in drafts:
        draft.delete()
    print(f"Черновики пользователя id={user} удален")
    return HttpResponse('')
