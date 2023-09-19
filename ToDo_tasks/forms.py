from .models import TaskModel, ObjectModel, ContractModel, StageModel, OrdersModel, Employee, CanAcceptModel, \
    WorkerModel, ApproveModel, AttachmentFilesModel, CommandNumberModel, MarkDocModel, FavoritesListModel, \
    FavoritesShareModel, TasksInFavoritesModel, DraftTaskModel
from django.forms import ModelForm, TextInput, Textarea, CheckboxInput, Select, ChoiceField, Form, PasswordInput, \
    CharField, ModelChoiceField, modelformset_factory, ModelMultipleChoiceField, MultipleChoiceField, SelectMultiple, \
    FileField, ClearableFileInput, FileInput, DateTimeField, DateTimeInput
from django.contrib.auth.forms import AuthenticationForm, UsernameField

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
            "task_approved",
            "have_connection"
        ]
        widgets = {"task_order": Select(attrs={"class": "form-select",
                                               "aria-label": "Номер заказа"}),
                   "task_object": Select(attrs={"class": "form-select",
                                                "aria-label": "Наименование объекта",
                                                "style": "height: 125px;", "onchange": "checkParams()"}),
                   "task_contract": Select(attrs={"class": "form-select",
                                                  "aria-label": "Номер контракта",
                                                  'disabled': 'disabled', "onchange": "checkParams()"}),
                   "task_stage": Select(attrs={"class": "form-select",
                                               "aria-label": "Этап договора",
                                               'disabled': 'disabled'}),
                   "text_task": Textarea(attrs={"placeholder": "Введите текст задания",
                                                "class": "form-control",
                                                "style": "height:442px;", "onchange": "checkParams()"}),
                   "task_type_work": Select(attrs={"class": "form-select",
                                                   "aria-label": "Вид документации", "onchange": "checkParams()"}),
                   "first_sign_user": Select(attrs={"class": "form-select",
                                                    "aria-label": "Первый руководитель",
                                                    "style": "width: 500px;", "onchange": "checkParams()"}),
                   "second_sign_user": Select(attrs={"class": "form-select",
                                                     "aria-label": "Второй руководитель",
                                                     "style": "width: 500px;", "onchange": "checkParams()"}),
                   "task_mark_doc": Select(attrs={"class": "form-select",
                                                  "aria-label": "Марка документации", "onchange": "checkParams()"}),
                   # "cpe_sign_user": Select(attrs={"class": "form-select",
                   #                                "aria-label": "ГИП"}),
                   "incoming_dep": SelectMultiple(attrs={"class": "form-select",
                                                         "aria-label": "Отдел принимающий задание",
                                                         "style": "width: 500px;", "onchange": "checkParams()"}),
                   "task_building": TextInput(attrs={"class": "form-control",
                                                     "aria-label": "Здание", "onchange": "checkParams()"}),
                   "task_need_approve": CheckboxInput()
                   }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['task_order'].queryset = OrdersModel.objects.order_by('order')
        self.fields['incoming_dep'].queryset = CommandNumberModel.objects.filter(show=True).order_by('command_number')
        self.fields['task_object'].queryset = ObjectModel.objects.filter(show=True).order_by('object_name')
        self.fields['task_mark_doc'].queryset = MarkDocModel.objects.order_by("mark_doc")
        self.fields['task_contract'].queryset = ContractModel.objects.filter(show=True).order_by("contract_name")  # подгрузка значений
        self.fields['task_stage'].queryset = StageModel.objects.order_by("stage_name")  # подгрузка значений
        self.fields['task_contract'].choices = [(0, 'Сначала выберете объект')]  # исходное отображение
        self.fields['task_stage'].choices = [(0, 'Сначала выберете № договора')]  # исходное отображение


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
            'task_approved',
            'have_connection'

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
                   "task_mark_doc": Select(attrs={"class": "form-select",
                                                  "aria-label": "Марка документации"}),
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
        widgets = {"task_order": TextInput(attrs={"class": "form-select",
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
                   "task_mark_doc": TextInput(attrs={"class": "form-control",
                                                     "aria-label": "Марка документации",
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
            'incoming_employee',
            "cpe_sign_user",
            'have_connection'
        ]
        widgets = {"task_building": TextInput(attrs={"class": "form-control",
                                                     "aria-label": "Здание", "onchange": "checkParams()"}),
                   "text_task": Textarea(attrs={"placeholder": "Введите текст задания",
                                                "class": "form-control", "onchange": "checkParams()"}),
                   "first_sign_user": Select(attrs={"class": "form-select",
                                                    "aria-label": "Первый руководитель", "onchange": "checkParams()"}),
                   "second_sign_user": Select(attrs={"class": "form-select",
                                                     "aria-label": "Второй руководитель", "onchange": "checkParams()"}),
                   # "cpe_sign_user": Select(attrs={"class": "form-select",
                   #                                "aria-label": "ГИП"}),
                   "incoming_dep": Select(attrs={"class": "form-select",
                                                 "aria-label": "Кому", "onchange": "checkParams()"}),
                   }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['incoming_dep'].queryset = CommandNumberModel.objects.filter(show=True).order_by('command_number')



class DateInput(DateTimeInput):
    input_type = 'date'


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
    task_contract = ModelChoiceField(widget=Select(attrs={"class": "form-select",
                                                          'disabled': 'disabled'}),
                                     queryset=ContractModel.objects,
                                     empty_label="Не выбрано",
                                     required=False)
    task_stage = ModelChoiceField(widget=Select(attrs={"class": "form-select",
                                                       'disabled': 'disabled'}),
                                  queryset=StageModel.objects,
                                  empty_label="Не выбрано",
                                  required=False)
    task_building = CharField(widget=TextInput(attrs={"class": "form-control",
                                                      "placeholder": "Здание"}),
                              required=False)
    task_dep = ModelChoiceField(widget=Select(attrs={"class": "form-select"}),
                                queryset=CommandNumberModel.objects,
                                empty_label="Не выбрано",
                                required=False)
    task_incoming_dep = ModelChoiceField(widget=Select(attrs={"class": "form-select"}),
                                         queryset=CommandNumberModel.objects,
                                         empty_label="Не выбрано",
                                         required=False)
    choice_type_work = [(0, 'Не выбрано'), (1, 'РД'), (2, 'ПД')]
    type_work = ChoiceField(widget=Select(attrs={"class": "form-select"}),
                            choices=choice_type_work,
                            # empty_label="Не выбрано",
                            required=False)
    choice_status = [(2, 'Актуально'), (1, 'На подписании'), (3, 'На корректировке'), (0, 'Аннулировано')]
    task_status = ChoiceField(widget=Select(attrs={"class": "form-select"}),
                              choices=choice_status,
                              required=False)
    date_start = DateTimeField(widget=DateInput(attrs={"class": "form-control"}), required=False)
    date_end = DateTimeField(widget=DateInput(attrs={"class": "form-control"}), required=False)

    task_text = CharField(widget=TextInput(attrs={"class": "form-control",
                                                  "placeholder": "Для кириллицы учитывайте регистр"}), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['task_contract'].queryset = ContractModel.objects  # подгрузка значений
        self.fields['task_stage'].queryset = StageModel.objects  # подгрузка значений
        self.fields['task_contract'].choices = [(0, 'Сначала выберете объект')]  # исходное отображение
        self.fields['task_stage'].choices = [(0, 'Сначала выберете № договора')]  # исходное отображение


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
                                         "aria-label": "Работник"}),
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
                                  "aria-label": "Работник"}),
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
                                                  "aria-label": "Согласователь",
                                                  "style": "width: 500px"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['approve_user'].queryset = Employee.objects.filter(work_status=True).order_by('last_name')


class FilesUploadForm(ModelForm):
    class Meta:
        model = AttachmentFilesModel
        fields = ['file']

        widgets = {
            'file': ClearableFileInput(attrs={'multiple': True,
                                              "class": "form-control",
                                              "style": "min-width: 500px;"
                                              })
        }


class ApproveEditForm(ModelForm):
    class Meta:
        model = ApproveModel
        fields = ['approve_user']

        widgets = {
            'approve_user': Select(attrs={"class": "form-select",
                                          "aria-label": "Первый руководитель"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['approve_user'].queryset = Employee.objects.filter(work_status=True).order_by('last_name')


class ApproveFormForSave(ModelForm):
    """Форма для добавления согласователей """

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['approve_user'].queryset = Employee.objects.filter(work_status=True).order_by('last_name')


class UserProfileForm(ModelForm):
    """Форма с данными пользователя"""

    class Meta:
        model = Employee
        exclude = ['user',
                   'right_to_sign',
                   'check_edit',
                   'can_make_task',
                   'cpe_flag',
                   'mailing_list_check'
                   ]
        widgets = {
            # 'user': Select(attrs={"class": "form-control",
            #                       "aria-label": "Имя пользователя",
            #                       "readonly": True,
            #                       'disable': True}),
            'last_name': TextInput(attrs={"class": "form-control",
                                          "aria-label": "Фамилия"
                                          }),
            'first_name': TextInput(attrs={"class": "form-control",
                                           "aria-label": "Имя"
                                           }),
            'middle_name': TextInput(attrs={"class": "form-control",
                                            "aria-label": "Отчество"
                                            }),
            "personnel_number": TextInput(attrs={"class": "form-control",
                                                 "aria-label": "Табельный номер"
                                                 }),
            "job_title": Select(attrs={"class": "form-select",
                                       "aria-label": "Должность"}),
            "department_group": Select(attrs={"class": "form-select",
                                              "aria-label": "Управление"}),
            "department": Select(attrs={"class": "form-select",
                                        "aria-label": "Управление"}),
            'user_phone': TextInput(attrs={"class": "form-control",
                                           "aria-label": "Отчество"
                                           }),
        }

    # WorkerFormSet = modelformset_factory(WorkerModel, fields=("worker_user",), extra=1, can_delete=False)
    WorkerFormSet = modelformset_factory(WorkerModel, form=WorkerForm)


class LoginForm(AuthenticationForm):
    username = UsernameField(
        widget=TextInput(
            attrs={"autofocus": True, "class": "form-control", 'id': 'floatingInput',
                   'placeholder': 'Имя пользователя'}))
    password = CharField(
        label=("Password"),
        strip=False,
        widget=PasswordInput(
            attrs={"autocomplete": "current-password", "class": "form-control", 'id': 'floatingPassword',
                   'placeholder': 'Пароль'}),
    )


class CreateFavoriteListForm(ModelForm):
    """Форма создания списков избранного"""

    class Meta:
        model = FavoritesListModel
        fields = ['favorite_list_name',
                  ]

        widgets = {"favorite_list_name": TextInput(attrs={"class": "form-control",
                                                          "aria-label": "Название списка"
                                                          })}


class ShareFavoriteListForm(ModelForm):
    class Meta:
        model = FavoritesShareModel
        fields = ['favorite_share_user',
                  'can_change_list']
        widgets = {"favorite_share_user": Select(attrs={"class": "form-select",
                                                        "aria-label": "Сотрудник"
                                                        }),
                   "can_change_list": CheckboxInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['favorite_share_user'].queryset = Employee.objects.order_by("last_name").filter(work_status=True)


class AddMyFavoriteForm(ModelForm):
    """Форма создания списков избранного"""

    class Meta:
        model = TasksInFavoritesModel
        fields = ['favorite_list',
                  ]

        widgets = {"favorite_list": Select(attrs={"class": "form-select",
                                                  "aria-label": "Сотрудник"
                                                  })}


class AddShareFavoriteForm(ModelForm):
    """Форма создания списков избранного"""

    class Meta:
        model = TasksInFavoritesModel
        fields = ['favorite_list',
                  ]

        widgets = {"favorite_list": Select(attrs={"class": "form-select",
                                                  "aria-label": "Сотрудник"
                                                  })}


class SaveDraftForm(ModelForm):
    """Форма создания списков избранного"""

    class Meta:
        model = DraftTaskModel
        fields = ['draft_name',
                  ]

        widgets = {"draft_name": TextInput(attrs={"class": "form-control",
                                                 "aria-label": "Название черновика"
                                                 })}
