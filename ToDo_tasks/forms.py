
from .models import TaskModel, ObjectModel, ContractModel, StageModel, OrdersModel, Employee, CanAcceptModel
from django.forms import ModelForm, TextInput, Textarea, CheckboxInput, Select, modelformset_factory, ChoiceField, Form, CharField, ModelChoiceField

from django.views import View


class TaskForm(ModelForm):
    class Meta:
        model = TaskModel
        # fields = '__all__'
        exclude = [
            "author",
            'department_number',
            'task_number',
            'task_change_number',
            "first_sign_status",
            "second_sign_status",
            "cpe_sign_status",
            "back_to_change",
            "first_sign_date",
            "second_sign_date",
            "cpe_sign_date",
            "task_status",
            "task_last_edit",
            "cpe_comment",
            "incoming_date",
            "incoming_dep",
            "task_workers"
        ]
        widgets = {"task_order": Select(attrs={"class": "form-select",
                                               "aria-label": "Номер заказа"}),
                   "task_object": Select(attrs={"class": "form-select",
                                                "aria-label": "Наименование объекта"}),
                   "task_contract": Select(attrs={"class": "form-select",
                                                  "aria-label": "Номер контракта"}),
                   "task_stage": Select(attrs={"class": "form-select",
                                               "aria-label": "Этап договора"}),
                   "text_task": Textarea(attrs={"placeholder": "Введите текст задания",
                                                "class": "form-control"}),
                   "task_type_work": Select(attrs={"class": "form-select",
                                                   "aria-label": "Вид документации"}),
                   "first_sign_user": Select(attrs={"class": "form-select",
                                                    "aria-label": "Первый руководитель"}),
                   "second_sign_user": Select(attrs={"class": "form-select",
                                                     "aria-label": "Второй руководитель"}),
                   "cpe_sign_user": Select(attrs={"class": "form-select",
                                                  "aria-label": "ГИП"}),
                   "incoming_dep": Select(attrs={"class": "form-select",
                                               "aria-label": "Отдел принимающий задание"}),
                   "incoming_employee": Select(attrs={"class": "form-select",
                                                  "aria-label": "Кому"}),
                   }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['task_contract'].queryset = ContractModel.objects  # подгрузка значений
        self.fields['task_stage'].queryset = StageModel.objects  # подгрузка значений
        self.fields['task_contract'].choices = [(0, '---------')]  # исходное отображение
        self.fields['task_stage'].choices = [(0, '---------')]  # исходное отображение



class TaskCheckForm(ModelForm):
    # todo Доделать просмотр подробностей
    class Meta:
        model = TaskModel
        exclude = ['department_number', 'task_number', 'task_change_number', "first_sign_status",
                   "second_sign_status", "cpe_sign_status", "back_to_change"]
        widgets = {"task_order": Select(attrs={"class": "form-select",
                                               "disabled": True}),
                   "author": TextInput(attrs={"class": "form-control",
                                              "readonly": True}),
                   "task_object": TextInput(attrs={"class": "form-select",
                                                   "disabled": True}),
                   "task_contract": TextInput(attrs={"class": "form-select",
                                                     "disabled": True}),
                   "task_stage": TextInput(attrs={"class": "form-select",
                                                  "disabled": True}),
                   "text_task": Textarea(attrs={"class": "form-control",
                                                "type": "text",
                                                "value": "Disabled readonly input",
                                                "aria-label": "Disabled input example",
                                                "readonly": True}),
                   "incoming_employee": TextInput(attrs={"class": "form-control",
                                              "readonly": True})
                   }


class TaskEditForm(ModelForm):
    """Форма для внесения изменений в задание"""
    class Meta:
        model = TaskModel
        # fields = '__all__'
        exclude = [
            "author",
            'department_number',
            'task_number',
            'task_change_number',
            "first_sign_status",
            "second_sign_status",
            "cpe_sign_status",
            "back_to_change",
            "first_sign_date",
            "second_sign_date",
            "cpe_sign_date",
            "task_status",
            "task_last_edit",
            "cpe_comment",
            "incoming_date",
            "incoming_dep",
            "task_workers",
            'task_order',
            'task_object',
            'task_contract',
            'task_stage',
            'task_type_work',
        ]
        widgets = {"text_task": Textarea(attrs={"placeholder": "Введите текст задания",
                                                "class": "form-control"}),
                   "first_sign_user": Select(attrs={"class": "form-select",
                                                    "aria-label": "Первый руководитель"}),
                   "second_sign_user": Select(attrs={"class": "form-select",
                                                     "aria-label": "Второй руководитель"}),
                   "cpe_sign_user": Select(attrs={"class": "form-select",
                                                  "aria-label": "ГИП"}),
                   "incoming_employee": Select(attrs={"class": "form-select",
                                                  "aria-label": "Кому"}),
                   }


class SearchForm(Form):

    task_order = ModelChoiceField(widget=Select(attrs={"class": "form-select",
                                               "aria-label": "Номер заказа"}),
                                  queryset=OrdersModel.objects,
                                  empty_label="Не выбрано",
                                  required=False)
    task_object = ModelChoiceField(widget=Select(attrs={"class": "form-select"}),
                                   queryset=ObjectModel.objects,
                                   empty_label="Не выбрано",
                                  required=False)
    task_contract = ModelChoiceField(widget=Select(attrs={"class": "form-select"}),
                                     queryset=ContractModel.objects,
                                     empty_label="Не выбрано",
                                     required=False)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['task_contract'].queryset = ContractModel.objects  # подгрузка значений
        self.fields['task_contract'].choices = [(0, '---------')]
