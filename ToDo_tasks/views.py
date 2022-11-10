from django.shortcuts import render, redirect
from django.views import View
from .models import Employee, TaskModel, ContractModel, ObjectModel, StageModel
from .forms import TaskForm, TaskCheckForm


class IndexView(View):
    """Главная страница"""
    def get(self, request):
        """
        Проверяет авторизацию пользователя и выводит данные на странице,
        либо redirect на страницу авторизации
        """
        if request.user.is_authenticated:
            # Получаем список заданий пользователя
            data_user = TaskModel.objects.get_queryset().filter(author__user=request.user)
            # Получаем список всех заданий
            data_all = TaskModel.objects.get_queryset()
            # Получаем информацию о пользователе из таблицы Employee на основании request
            user = Employee.objects.get(user=request.user)
            print(request.user)  # login
            print(user)  # Фамилия Имя
            content = {'data_user': data_user,
                       'data_all': data_all,
                       'user': user}
            return render(request, 'todo_tasks/index.html', content)
        else:
            return redirect('login/')


class DetailView(View):
    def get(self, request, pk):
        obj = TaskModel.objects.get(pk=pk)
        data = {"text_task": obj.text_task}
        form = TaskCheckForm(initial=data)
        user = Employee.objects.get(user=request.user)
        content = {'obj': obj,
                   'user': user,
                   'form': form}
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
            last_task = TaskModel.objects.all().filter(task_change_number=None).filter(
                department_number=new_post.author.department)
            # Формируем номер нового задания
            number_task_new = int(last_task.latest('task_number').task_number.split('-')[2]) + 1
            new_post.task_number = f'ЗД-{new_post.department_number}-{number_task_new}'
            print(new_post.task_number)
            print(new_post)
            form.save()  # сохраняем форму в бд
            return redirect('index')
        return redirect('index')


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

