from .models import TaskModel, ObjectModel, ContractModel, StageModel, OrdersModel, Employee, CanAcceptModel, \
    WorkerModel, ApproveModel, AttachmentFilesModel
from django.forms import ModelForm, TextInput, Textarea, CheckboxInput, Select, ChoiceField, Form, \
    CharField, ModelChoiceField, modelformset_factory, ModelMultipleChoiceField, MultipleChoiceField, SelectMultiple, FileField, ClearableFileInput, FileInput

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
            "incoming_employee",
            "task_workers",
            "cpe_sign_user",
            "task_approved"
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
                   # "cpe_sign_user": Select(attrs={"class": "form-select",
                   #                                "aria-label": "ГИП"}),
                   "incoming_dep": SelectMultiple(attrs={"class": "form-select",
                                                    "aria-label": "Отдел принимающий задание"}),
                   "task_building": TextInput(attrs={"class": "form-control",
                                                     "aria-label": "Здание"}),
                   "task_need_approve": CheckboxInput()
                   }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['task_contract'].queryset = ContractModel.objects  # подгрузка значений
        self.fields['task_stage'].queryset = StageModel.objects  # подгрузка значений
        self.fields['task_contract'].choices = [(0, '---------')]  # исходное отображение
        self.fields['task_stage'].choices = [(0, '---------')]  # исходное отображение


class TaskFormForSave(ModelForm):
    """Форма для сохранения данных с раздела выдать задание.
    Необходима для обхода проблем с проверкой поля отдела, куда выдается задание
    """
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
            "incoming_employee",
            "task_workers",
            "cpe_sign_user",
            'task_approved'
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
                   # "cpe_sign_user": Select(attrs={"class": "form-select",
                   #                                "aria-label": "ГИП"}),
                   "incoming_dep": Select(attrs={"class": "form-select",
                                                    "aria-label": "Отдел принимающий задание"}),
                   "task_building": TextInput(attrs={"class": "form-control",
                                                     "aria-label": "Здание"}),
                   "task_need_approve": CheckboxInput()
                   }




class TaskCheckForm(ModelForm):
    # todo Доделать просмотр подробностей
    class Meta:
        model = TaskModel
        exclude = ['department_number', 'task_number', 'task_change_number', "first_sign_status",
                   "second_sign_status", "cpe_sign_status", "back_to_change", 'incoming_employee']
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
                                                "readonly": True}),
                   "incoming_dep": TextInput(attrs={"class": "form-control",
                                                    "readonly": True}),
                   "task_building": TextInput(attrs={"class": "form-control",
                                                     "aria-label": "Здание",
                                                     "readonly": True}),
                   "task_type_work": TextInput(attrs={"class": "form-select",
                                                      "disabled": True}),
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
            "task_workers",
            'task_order',
            'task_object',
            'task_contract',
            'task_stage',
            'task_type_work',
            "task_building",
            'incoming_employee',
            "cpe_sign_user"
        ]
        widgets = {"text_task": Textarea(attrs={"placeholder": "Введите текст задания",
                                                "class": "form-control"}),
                   "first_sign_user": Select(attrs={"class": "form-select",
                                                    "aria-label": "Первый руководитель"}),
                   "second_sign_user": Select(attrs={"class": "form-select",
                                                     "aria-label": "Второй руководитель"}),
                   # "cpe_sign_user": Select(attrs={"class": "form-select",
                   #                                "aria-label": "ГИП"}),
                   "incoming_dep": Select(attrs={"class": "form-select",
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


class TaskEditWorkersForm(ModelForm):
    """Форма для выбора задания для смены ответственных исполнителей"""
    class Meta:
        model = TaskModel
        fields = ["task_number", ]
        widgets = {
            "task_number": Select(attrs={"class": "form-select",
                                         "aria-label": "Задание"}),
        }

class WorkerForm(ModelForm):
    """Форма для назначения ответственных на странице деталей"""
    class Meta:
        model = WorkerModel
        exclude = ['task',
                   'read_status'
                   ]
        widgets = {
            "worker_user": Select(attrs={"class": "form-select",
                                         "aria-label": "Первый руководитель"}),
        }


class WorkersEditForm(ModelForm):
    """Формат для назначения ответственных на странице редактирования ответственных"""
    class Meta:
        model = WorkerModel
        exclude = ['worker_user',
                   'read_status'
                   ]
        widgets = {
            "task": Select(attrs={"class": "form-select",
                                         "aria-label": "Первый руководитель"}),
        }


class ApproveForm(ModelForm):
    """Форма для выбора согласователей"""
    class Meta:
        model = ApproveModel
        exclude = [
            'approve_task',
            'approve_status',
            'approve_date',
        ]
        widgets = {
            "approve_user": SelectMultiple(attrs={"class": "form-select",
                                                  "aria-label": "Согласователь"}),
        }

class FilesUploadForm(ModelForm):
    class Meta:
        model = AttachmentFilesModel
        fields = ['file']

        widgets = {
            'file': ClearableFileInput(attrs={'multiple': True})
        }

class ApproveFormForSave(ModelForm):
    """Форма для """
    class Meta:
        model = ApproveModel
        exclude = [
            'approve_task',
            'approve_status',
            'approve_date',
        ]
        widgets = {
            "approve_user": Select(attrs={"class": "form-select",
                                                  "aria-label": "Согласователь"}),
        }

# WorkerFormSet = modelformset_factory(WorkerModel, fields=("worker_user",), extra=1, can_delete=False)
WorkerFormSet = modelformset_factory(WorkerModel, form=WorkerForm)
