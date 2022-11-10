from .models import TaskModel, ObjectModel, ContractModel, StageModel, OrdersModel, Employee
from django.forms import ModelForm, TextInput, Textarea, CheckboxInput, Select, modelformset_factory, ChoiceField


from django.views import View


class TaskForm(ModelForm):
    class Meta:
        model = TaskModel
        # fields = '__all__'
        exclude = ["author", 'department_number', 'task_number', 'task_change_number', "first_sign_status",
                   "second_sign_status", "cpe_sign_status", "back_to_change"]
        widgets = {"task_order": Select(attrs={"class": "form-select",
                                               "aria-label": "Номер заказа"}),
                   "task_object": Select(attrs={"class": "form-select",
                                                "aria-label": "Наименование объекта"}),
                   "task_contract": Select(attrs={"class": "form-select",
                                                  "aria-label": "Номер контракта"}),
                   "task_stage": Select(attrs={"class": "form-select",
                                               "aria-label": "Этап договора"}),
                   "text_task": Textarea(attrs={"placeholder": "Введите текст",
                                                "class": "form-control"}),
                   "task_type_work": Select(attrs={"class": "form-select",
                                                   "aria-label": "Вид документации"}),
                   "first_sign_user": Select(attrs={"class": "form-select",
                                                    "aria-label": "Первый руководитель"}),
                   "second_sign_user": Select(attrs={"class": "form-select",
                                                     "aria-label": "Второй руководитель"}),
                   "cpe_sign_user": Select(attrs={"class": "form-select",
                                                  "aria-label": "ГИП"}),
                   }

    def __init__(self, *args, **kwargs):
        department_id = kwargs.pop('department_user', None)
        super().__init__(*args, **kwargs)
        self.fields['task_contract'].queryset = ContractModel.objects  # подгрузка значений
        self.fields['task_stage'].queryset = StageModel.objects  # подгрузка значений
        self.fields['task_contract'].choices = [(0, '---------')]  # исходное отображение
        self.fields['task_stage'].choices = [(0, '---------')]  # исходное отображение
        # self.fields['first_sign_user'].queryset = Employee.objects.filter(department=department_id).filter(right_to_sign=True)
        # load_department_signature(self.data)

        if 'task_object' in self.data:
            try:
                object_id = int(self.data.get('task_object'))
                self.fields['task_contract'].queryset = ContractModel.objects.filter(contract_object=object_id)
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset

        print(self.data)


class TaskCheckForm(ModelForm):
    # todo Доделать просмотр подробностей
    class Meta:
        model = TaskModel
        exclude = ["author", 'department_number', 'task_number', 'task_change_number', "first_sign_status",
                   "second_sign_status", "cpe_sign_status", "back_to_change"]
        widgets = {"task_order": Select(attrs={"class": "form-select",
                                               "aria-label": "Номер заказа"}),
                   "task_object": Select(attrs={"class": "form-select",
                                                "aria-label": "Наименование объекта"}),
                   "task_contract": Select(attrs={"class": "form-select",
                                                  "aria-label": "Номер контракта"}),
                   "task_stage": Select(attrs={"class": "form-select",
                                               "aria-label": "Этап договора",
                                               "placeholder": "Disabled input"}),
                   "text_task": Textarea(attrs={"class": "form-control",
                                                "type": "text",
                                                "value": "Disabled readonly input",
                                                "aria-label": "Disabled input example",
                                                "readonly": True})
                   }
