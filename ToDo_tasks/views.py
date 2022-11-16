from django.shortcuts import render, redirect
from django.views import View

from .models import Employee, TaskModel, ContractModel, ObjectModel, StageModel
from .forms import TaskForm, TaskCheckForm
from .functions import get_signature_info, get_data_for_form, get_data_for_detail, get_list_to_sign


class IndexView(View):
    """Главная страница"""

    def get(self, request):
        """
        Проверяет авторизацию пользователя и выводит данные на странице,
        либо redirect на страницу авторизации
        """
        if request.user.is_authenticated:
            if request.user.id == 1:
                return redirect('admin/')
            # Получаем список заданий пользователя
            # data_user = TaskModel.objects.get_queryset().filter(author__user=request.user)
            # Получаем список всех заданий
            data_all = TaskModel.objects.get_queryset()
            # Получаем информацию о пользователе из таблицы Employee на основании request
            user = Employee.objects.get(user=request.user)
            count_task_to_sign = 0
            if user.right_to_sign == True:
                count_task_to_sign = len(get_list_to_sign(user))  # Получение количества заданий ожидающих подписи
            print(request.user)  # login
            print(user)  # Фамилия Имя
            content = {'data_all': data_all,
                       'user': user,
                       "count_task_to_sign": f'({count_task_to_sign})'}
            return render(request, 'todo_tasks/index.html', content)
        else:
            return redirect('login/')


class UserTaskView(View):
    def get(self, request):
        data_user = TaskModel.objects.get_queryset().filter(author__user=request.user)
        user = Employee.objects.get(user=request.user)
        content = {'data_user': data_user,
                   'user': user}
        return render(request, 'todo_tasks/my_tasks.html', content)


class DetailView(View):
    """Формирование страницы просмотра деталей"""

    def get(self, request, pk):
        """Получаем номер задания из ссылки и формируем страницу подробностей"""
        content = get_data_for_detail(request, pk)
        return render(request, 'todo_tasks/details.html', content)


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
        objects = ObjectModel.objects.all()
        context = {'form': form,
                   'user': Employee.objects.get(user=request.user),
                   'objects': objects}
        return render(request, 'todo_tasks/add_task.html', context)

    def post(self, request):
        form = TaskForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)  # отменяем отправку form в базу
            new_post.author = Employee.objects.get(user=request.user)  # добавляем пользователя из request
            new_post.department_number = new_post.author.department  # добавляем номер отдела пользователя
            # Получаем номер последнего задания. Сначала фильтруем задания без изменений, затем по номеру отдела
            last_task = TaskModel.objects.all().filter(task_change_number=0).filter(
                department_number=new_post.author.department)
            # Формируем номер нового задания
            number_task_new = int(last_task.latest('task_number').task_number.split('-')[2]) + 1
            new_post.task_number = f'ЗД-{new_post.department_number}-{number_task_new}'
            new_post.task_change_number = 0  # номер изменения присваиваем 0
            print(new_post.task_number)
            form.save()  # сохраняем форму в бд
            # После сохранения получаем id записи в бд, для формирования ссылки
            number_id_for_redirect = TaskModel.objects.get(task_number=new_post.task_number).id
            return redirect(f'/details/{number_id_for_redirect}')
        return redirect('index')


class EditTaskView(View):
    """
    Страница редактирования записи.
    Реализация через UpdateView не возможна, так как в исходном class AddTask формируется номер нового задания,
    а нам необходимо обновить данные уже существующего
    """

    def get(self, request, pk):
        """Получаем номер редактируемого задания из query params (pk) и заполняем форму с данными из бд"""
        obj = TaskModel.objects.get(pk=pk)
        form = TaskForm(instance=obj)

        department_user = Employee.objects.get(user=request.user).department
        form.fields['first_sign_user'].queryset = Employee.objects.filter(department=department_user).filter(
            right_to_sign=True)  # получаем в 1ое поле список пользователей по двум фильтрам
        form.fields['second_sign_user'].queryset = Employee.objects.filter(department=department_user).filter(
            right_to_sign=True)  # получаем во 2ое поле список пользователей по двум фильтрам

        context = {
            'form': form,
            'user': Employee.objects.get(user=request.user),
            'obj': obj
        }
        return render(request, 'todo_tasks/update_task.html', context)

    def post(self, request, pk):
        """Обновляем данные базы данных"""
        form = TaskForm(request.POST)

        # if form.is_valid():
        obj = TaskModel.objects.get(pk=pk)  # Получаем объект из бд
        # Присваиваем вручную новые данные из формы, почему только так работает, сказать не могу
        # Номер задания и автор остаются исходными
        obj.task_object.id = form.data['task_object']
        obj.task_contract.id = form.data['task_contract']
        obj.task_stage.id = form.data['task_stage']
        obj.task_order.id = form.data['task_stage']
        obj.task_type_work = form.data['task_type_work']
        obj.text_task = form.data['text_task']
        print(form.data['first_sign_user'])
        obj.first_sign_user_id = form.data['first_sign_user']
        obj.second_sign_user_id = form.data['second_sign_user']
        obj.cpe_sign_user_id = form.data['cpe_sign_user']
        # На случай, если задание было возвращено, обнуляем значения подписей и флаг back_to_change
        obj.first_sign_status = 0
        obj.second_sign_status = 0
        obj.cpe_sign_status = 0
        obj.back_to_change = 0
        # Сохраняем новые данные в базу данных
        obj.save()

        print(f"сработал пост{pk}")
        return redirect(f'/details/{pk}')


class ToSignListView(View):
    """Страница со списком заданий ожидающих подписи"""

    def get(self, request):
        sign_user = Employee.objects.get(user=request.user)  # получаем пользователя
        sign_list = get_list_to_sign(sign_user)  # получаем список заданий
        content = {
            'sign_list': sign_list,
            'user': sign_user}
        return render(request, 'todo_tasks/incoming_to_sign.html', content)


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
            obj.save()
        elif 'sign2' in request.POST:
            obj.second_sign_status = True
            obj.save()
            print(pk, ' sign')
        elif 'cancel1' in request.POST:
            print(pk, ' cancel1')
            obj.first_sign_status = False
            obj.save()
        elif 'cancel2' in request.POST:
            print(pk, ' cancel1')
            obj.second_sign_status = False
            obj.save()
        elif 'back_to_change' in request.POST:
            obj.back_to_change = True
            obj.save()
            print(pk, ' back to change')
            return redirect('incoming_to_sign')
        elif 'testmodal' in request.POST:
            print(request.POST.get('text_modal_rows'))
        return redirect(request.META['HTTP_REFERER'])


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
