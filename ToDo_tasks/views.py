import datetime

from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View
from django.db.models import Q

from .models import Employee, TaskModel, ContractModel, ObjectModel, StageModel, TaskNumbersModel, CommandNumberModel, \
    CpeModel, CanAcceptModel, BackCommentModel, WorkerModel
from .forms import TaskForm, TaskCheckForm, TaskEditForm, SearchForm, WorkerFormSet
from .functions import get_signature_info, get_data_for_form, get_data_for_detail, get_list_to_sign, get_task_edit_form


def check_user_status(request):
    user = Employee.objects.get(user=request.user)
    return user


class IndexView(View):
    """Главная страница"""

    def get(self, request):
        """
        Проверяет авторизацию пользователя и выводит данные на странице,
        либо redirect на страницу авторизации
        """
        # Что бы не падало в ошибку, проверяем авторизацию пользователя
        if request.user.is_anonymous:
            return redirect('login/')
        elif request.user.is_superuser:
            return redirect('admin/')

        # Получаем информацию о пользователе из таблицы Employee на основании request
        user = Employee.objects.get(user=request.user)

        count_task_to_sign = 0
        count_task_to_workers = 0
        if user.right_to_sign == True:
            count_task_to_sign = len(get_list_to_sign(user))  # Получение количества заданий ожидающих подписи
            count_task_to_workers = TaskModel.objects.get_queryset().filter(task_status=2).filter(
                incoming_dep=user.department).filter(task_workers=False).count()

        print(request.user)  # login
        print(user)  # Фамилия Имя
        content = {'user': user,
                   "count_task_to_sign": f'({count_task_to_sign})',
                   "count_task_to_workers": f'({count_task_to_workers})'}
        return render(request, 'todo_tasks/index.html', content)

    def post(self, request):
        if request.POST.get('search_field') == '':
            return redirect(request.META['HTTP_REFERER'])
        else:
            return redirect(f'search_result', request.POST.get('search_field'))


class IssuedTasksView(View):
    """Страница выданных заданий, уже всеми подписаны"""

    def get(self, request):
        user = Employee.objects.get(user=request.user)
        data_all = TaskModel.objects.get_queryset().filter(department_number=user.department).filter(~Q(task_status=1))
        content = {'data_all': data_all,
                   'user': user}
        return render(request, 'todo_tasks/issued_tasks.html', content)


class OutgoingTasksView(View):
    """Страница исходящих заданий, которые еще на подписи"""

    def get(self, request):
        user = Employee.objects.get(user=request.user)
        data_to_sign = TaskModel.objects.get_queryset().filter(department_number=user.department).filter(task_status=1)
        content = {'data_to_sign': data_to_sign,
                   'user': user}
        return render(request, 'todo_tasks/outgoing_tasks.html', content)


class IncomingDepView(View):
    """Страница входящих заданий по номеру отделу пользователя"""

    def get(self, request):
        user = Employee.objects.get(user=request.user)  # Получаем пользователя из запроса
        user_dep = user.department_id  # получаем id номер отдела
        data_have_workers = TaskModel.objects.get_queryset().filter(incoming_dep=user_dep).filter(task_status=2)
        content = {'data_have_workers': data_have_workers,
                   'user': user}
        return render(request, 'todo_tasks/incoming_to_dep.html', content)


class UserTaskView(View):
    """Просмотр выданных заданий """

    def get(self, request):
        data_user = TaskModel.objects.get_queryset().filter(author__user=request.user).filter(task_status=2)
        user = Employee.objects.get(user=request.user)
        text_status = f"выданные"
        content = {'data_user': data_user,
                   'user': user,
                   "text_status": text_status}
        return render(request, 'todo_tasks/my_tasks.html', content)


class UserTaskOnSignView(View):
    """Получение списка для страницы исходящих заданий"""

    def get(self, request):
        data_user = TaskModel.objects.get_queryset().filter(author__user=request.user).filter(task_status=1)
        user = Employee.objects.get(user=request.user)
        text_status = f"исходящие"
        content = {'data_user': data_user,
                   'user': user,
                   "text_status": text_status}
        return render(request, 'todo_tasks/my_tasks.html', content)


class DetailView(View):
    """Формирование страницы просмотра деталей"""

    def get(self, request, pk):
        """Получаем номер задания из ссылки и формируем страницу подробностей"""
        content = get_data_for_detail(request, pk)
        return render(request, 'todo_tasks/details.html', content)

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

    def get(self, request):
        form = TaskForm()
        # Фильтруем поля руководителей в соответствии с отделом пользователя
        department_user = Employee.objects.get(user=request.user).department  # получаем номер отдела
        form.fields['first_sign_user'].queryset = Employee.objects.filter(department=department_user).filter(
            right_to_sign=True)  # получаем в 1ое поле список пользователей по двум фильтрам
        form.fields['second_sign_user'].queryset = Employee.objects.filter(department=department_user).filter(
            right_to_sign=True)  # получаем во 2ое поле список пользователей по двум фильтрам
        form.fields[
            'cpe_sign_user'].queryset = CpeModel.objects.get_queryset().all()  # получаем во 2ое поле список пользователей по двум фильтрам
        form.fields['incoming_employee'].quryset = CanAcceptModel.objects.get_queryset().all()
        objects = ObjectModel.objects.all()
        context = {'form': form,
                   'user': Employee.objects.get(user=request.user),
                   'objects': objects}
        return render(request, 'todo_tasks/add_task.html', context)

    def post(self, request):
        form = TaskForm(request.POST)
        print(form.errors)
        if form.is_valid():
            new_post = form.save(commit=False)  # отменяем отправку form в базу
            new_post.author = Employee.objects.get(user=request.user)  # добавляем пользователя из request
            new_post.department_number = new_post.author.department  # добавляем номер отдела пользователя, пока не знаю зачем
            # Получаем номер последнего задания из таблицы TaskNumbers
            last_number = TaskNumbersModel.objects.get(command_number=new_post.department_number)
            print(last_number.count_of_task)
            print(last_number.year_of_task)
            today_year = datetime.datetime.today().year  # выносим в отдельную переменную, что бы каждый раз не вызывалась функция
            # Проверяем год. Если отличается от нынешнего, обнуляем счетчик заданий
            if last_number.year_of_task == today_year:
                last_number.count_of_task += 1
            else:
                last_number.year_of_task = today_year
                last_number.count_of_task = 1
            last_number.save()  # сохраняем в таблице счетчиков (TaskNumbersModel) обновленные данные

            new_post.task_last_edit = datetime.datetime.now()  # Присваиваем дату последнего изменения

            new_post.task_number = f'ЗД-{new_post.department_number.command_number}-{last_number.count_of_task}-{str(today_year)[2:4]}'
            new_post.task_change_number = 0  # номер изменения присваиваем 0
            print(new_post.task_number)
            form.save()  # сохраняем форму в бд
            # После сохранения получаем id записи в бд, для формирования ссылки
            number_id_for_redirect = TaskModel.objects.get(task_number=new_post.task_number).id
            return redirect(f'/details/{number_id_for_redirect}')
        return redirect('/')


class EditTaskView(View):
    """
    Страница редактирования записи.
    Реализация через UpdateView не возможна, так как в исходном class AddTask формируется номер нового задания,
    а нам необходимо обновить данные уже существующего
    """

    def get(self, request, pk):
        """Получаем номер редактируемого задания из query params (pk) и заполняем форму с данными из бд"""
        obj = TaskModel.objects.get(pk=pk)
        form = get_task_edit_form(request, obj)

        context = {
            'form': form,
            'user': Employee.objects.get(user=request.user),
            'obj': obj
        }
        return render(request, 'todo_tasks/update_task.html', context)

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
            print(form.data['first_sign_user'])
            obj.first_sign_user_id = form.data['first_sign_user']
            obj.second_sign_user_id = form.data['second_sign_user']
            obj.cpe_sign_user_id = form.data['cpe_sign_user']
            obj.incoming_employee_id = form.data['incoming_employee']
            # На случай, если задание было возвращено, обнуляем значения подписей и флаг back_to_change
            obj.first_sign_status = 0
            obj.second_sign_status = 0
            obj.cpe_sign_status = 0
            obj.back_to_change = 0
            obj.task_last_edit = timezone.now()  # обновляем дату последнего изменения
            # Сохраняем новые данные в базу данных
            obj.save()
            print(f"сработал пост{pk}")
            return redirect(f'/details/{pk}')


class AddChangeTaskView(View):
    """Выдать изменение к заданию"""

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

        return render(request, 'todo_tasks/add_task_change.html', context)

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
        # Присваиваем номер задания с изменением
        new_task_with_change.task_number = f'{changing_task.task_number}/И{new_task_with_change.task_change_number}'
        # Присваиваем данные из формы
        new_task_with_change.text_task = form.data['text_task']
        new_task_with_change.first_sign_user_id = form.data['first_sign_user']
        new_task_with_change.second_sign_user_id = form.data['second_sign_user']
        new_task_with_change.cpe_sign_user_id = form.data['cpe_sign_user']
        new_task_with_change.incoming_employee_id = form.data['incoming_employee']
        new_task_with_change.task_last_edit = timezone.now()
        new_task_with_change.save()
        # Получаем id выданного задания, для формирования ссылки
        number_id_for_redirect = TaskModel.objects.get(task_number=new_task_with_change.task_number).id
        return redirect(f'/details/{number_id_for_redirect}')


class ToSignListView(View):
    """Страница со списком заданий ожидающих подписи"""

    def get(self, request):
        sign_user = Employee.objects.get(user=request.user)  # получаем пользователя
        sign_list = get_list_to_sign(sign_user)  # получаем список заданий
        content = {
            'sign_list': sign_list,
            'user': sign_user}
        return render(request, 'todo_tasks/incoming_to_sign.html', content)


class ToWorkerListView(View):
    """Страница со списком заданий ожидающих назначить исполнителей"""

    def get(self, request):
        sign_user = Employee.objects.get(user=request.user)  # получаем пользователя
        user_dep = sign_user.department_id
        data_without_workers = TaskModel.objects.get_queryset().filter(incoming_dep=user_dep).filter(
            task_status=2).filter(task_workers=False)  # получаем список заданий
        print(data_without_workers)
        content = {
            'data_without_workers': data_without_workers,
            'user': sign_user}
        return render(request, 'todo_tasks/incoming_to_workers.html', content)


class ToSignDetailView(View):
    """Страница подписи задания"""

    def get(self, request, pk):
        content = get_data_for_detail(request, pk)
        return render(request, 'todo_tasks/details_to_sign.html', content)

    # Отработка кнопок подписи задания
    def post(self, request, pk):
        obj = TaskModel.objects.get(pk=pk)
        if 'sign1' in request.POST:
            print(pk, ' sign')
            obj.first_sign_status = True
            obj.first_sign_date = timezone.now()
            obj.save()
        elif 'sign2' in request.POST:
            obj.second_sign_status = True
            obj.second_sign_date = timezone.now()
            obj.save()
            print(pk, ' sign')
        elif 'sign3' in request.POST:
            obj.cpe_sign_status = True
            obj.cpe_sign_date = timezone.now()
            obj.task_status = 2
            obj.save()
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
            # obj =
        elif 'comment_modal_button' in request.POST:
            obj.cpe_sign_status = True
            obj.cpe_sign_date = timezone.now()
            obj.task_status = 2
            obj.cpe_comment = request.POST.get('comment_modal_text')
            obj.save()
            print(pk, request.POST.get('comment_modal_text'))
        return redirect(request.META['HTTP_REFERER'])


class ToAddWorkersDetailView(View):
    """Страница добавления ответственных"""

    def get(self, request, pk):
        content = get_data_for_detail(request, pk)
        formset = WorkerFormSet(queryset=Employee.objects.none())
        content["formset"] = formset
        return render(request, 'todo_tasks/details_to_add_workers.html', content)

    def post(self, request, pk):
        obj = TaskModel.objects.get(pk=pk)
        formset = WorkerFormSet(data=self.request.POST)
        if formset.is_valid():
            for f in formset:
                print(f.data)
                cd = f.cleaned_data
                hg = cd.get('worker_user').id
                print(cd)
                print(cd.get('worker_user'))
                print(hg)
        return redirect(request.META['HTTP_REFERER'])


class SearchView(View):
    """Отображение результатов поиска c главной страницы"""

    def get(self, request, pk):
        print(pk)
        """С главной страницы получаем ключ pk для поиска"""
        user = Employee.objects.get(user=request.user)
        search_result = TaskModel.objects.filter(
            Q(text_task__icontains=pk) | Q(task_number__icontains=pk) | Q(author__last_name__icontains=pk) | Q(
                task_building__icontains=pk))
        content = {"search_result": search_result,
                   "search_word": pk,
                   "user": user}
        return render(request, 'todo_tasks/search_result.html', content)


class AdvancedSearchView(View):
    def get(self, request):
        user = Employee.objects.get(user=request.user)
        form = SearchForm()
        content = {"user": user,
                   "form": form}
        return render(request, 'todo_tasks/advanced_search.html', content)

    def post(self, request):
        form = SearchForm(request.POST)
        print(form.data)
        return redirect(request.META['HTTP_REFERER'])


class AddWorkerView(View):
    def get(self, request):
        formset = WorkerFormSet(queryset=Employee.objects.none())
        content = {"formset": formset}
        return render(request, 'todo_tasks/test_cancel.html', content)

    def post(self, request):
        formset = WorkerFormSet(data=self.request.POST)
        if formset.is_valid():
            for f in formset:
                print(f.data)
                cd = f.cleaned_data
                hg = cd.get('worker_user').id
                print(cd)
                print(cd.get('worker_user'))
                print(hg)
        return redirect(request.META['HTTP_REFERER'])


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
