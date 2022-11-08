from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views import View
from .models import Employee, TaskModel, ContractModel, ObjectModel, StageModel
from .forms import TaskForm


class IndexView(View):
    def get(self, request):
        # user_dict = user.values()
        # print(user_dict)
        if request.user.is_authenticated:

            data_user = TaskModel.objects.get_queryset().filter(author__user=request.user)
            data_all = TaskModel.objects.get_queryset()
            user = Employee.objects.get(user=request.user)
            print(request.user)

            print(user)
            content = {'data_user': data_user,
                       'data_all': data_all,
                       'user': user}
            return render(request, 'todo_tasks/index.html', content)
        else:
            return redirect('login/')


class DetailView(View):
    def get(self, request, pk):
        obj = TaskModel.objects.get(pk=pk)
        content = {'obj': obj}
        return render(request, 'todo_tasks/details.html', content)


class AddTaskView(View):
    def get(self, request):
        form = TaskForm()
        objects = ObjectModel.objects.all()
        context = {'form': form,
                   'user': Employee.objects.get(user=request.user),
                   'objects': objects}
        return render(request, 'todo_tasks/add_task.html', context)

    def post(self, request):
        form = TaskForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = Employee.objects.get(user=request.user)
            new_post.department_number = new_post.author.department
            last_task = TaskModel.objects.all().filter(department_number=new_post.author.department)
            number_task_new = int(last_task.latest('task_number').task_number.split('-')[2]) + 1
            new_post.task_number = f'ЗД-{new_post.department_number}-{number_task_new}'
            print(new_post.task_number)
            print(new_post)
            form.save()
            return redirect('index')
        return redirect('index')


def load_contracts(request):
    print("ajax contract пришел")  # Проверка, сработал ли ajax с отправкой данных
    object_id = request.GET.get("object")  # достаем значение объекта из запроса
    contracts = ContractModel.objects.filter(
        contract_object=int(object_id))  # получаем все контракты для данного объекта
    print(contracts)  # Проверка полученных контрактов
    return render(request, 'todo_tasks/dropdown_update/contracts_dropdown_list_update.html', {'contracts': contracts})


def load_stages(request):
    print("ajax load пришел") # Проверка, сработал ли ajax с отправкой данных
    contract_id = request.GET.get("contract")
    stages = StageModel.objects.filter(stage_contract=int(contract_id))
    print(stages)
    return render(request, 'todo_tasks/dropdown_update/stages_dropdown_list_update.html', {'stages': stages})
#
