from .models import TaskModel, ObjectModel, ContractModel, StageModel, OrdersModel
from django.forms import ModelForm, TextInput, Textarea, CheckboxInput, Select, modelformset_factory, ChoiceField
from django.views import View


class TaskForm(ModelForm):
    class Meta:
        model = TaskModel
        # fields = '__all__'
        exclude = ["author", 'department_number', 'task_number', 'taas_change_number']
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
                                                   "aria-label": "Вид документации"})
                   }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['task_contract'].queryset = ContractModel.objects  # подгрузка значений
        self.fields['task_stage'].queryset = StageModel.objects  # подгрузка значений
        self.fields['task_contract'].choices = [(0, '---------')]  # исходное отображение
        self.fields['task_stage'].choices = [(0, '---------')]  # исходное отображение

        print(self.data)

        if 'task_object' in self.data:
            try:
                object_id = int(self.data.get('task_object'))
                self.fields['task_contract'].queryset = ContractModel.objects.filter(contract_object=object_id)
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        # elif self.instance.pk:
        #     self.fields['task_contract'].queryset = self.instance

# TaskFormSet = modelformset_factory(TaskModel, fields=("task_type_work", "text_task"), extra=1)
