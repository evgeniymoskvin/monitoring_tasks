from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.utils.translation import gettext_lazy as _
import datetime

COMAND_CHOICES = [(000, "000 - Не указан"), (201, "201 - Строительный первый"), (202, "202 - Строительный второй")]


class JobTitleModel(models.Model):
    """ Таблица должностей """

    job_title = models.CharField("Должность", max_length=200)

    class Meta:
        verbose_name = _("должность")
        verbose_name_plural = _("должности")

    def __str__(self):
        return f'{self.job_title}'


class CommandNumberModel(models.Model):
    """Номера отделов"""
    command_number = models.CharField("Номер отдела/Сокращение", max_length=15)
    command_name = models.CharField("Наименование отдела", max_length=150)

    def __str__(self):
        return f'{self.command_number}, {self.command_name}'

    class Meta:
        verbose_name = _("номер отдела")
        verbose_name_plural = _("номера отделов")


class Employee(models.Model):
    """
    Дополнительные параметры пользователей
    """

    class GroupDepartment(models.IntegerChoices):
        """Выбор управление"""
        UASP = 1, _("УАСП")
        USP = 2, _("УСП")

    user = models.OneToOneField(User, models.PROTECT, verbose_name="Пользователь")
    last_name = models.CharField("Фамилия", max_length=150)
    first_name = models.CharField("Имя", max_length=150)
    middle_name = models.CharField("Отчество", max_length=150)
    job_title = models.ForeignKey(JobTitleModel, on_delete=models.PROTECT, null=True, verbose_name="Должность")
    department = models.ForeignKey(CommandNumberModel, on_delete=models.PROTECT, null=True, verbose_name="№ отдела")
    user_phone = models.IntegerField("№ телефона")
    department_group = models.IntegerField(verbose_name="Управление", default=None, choices=GroupDepartment.choices)
    right_to_sign = models.BooleanField(verbose_name="Право подписывать", default=False)
    check_edit = models.BooleanField("Возможность редактирования", default=False)
    can_make_task = models.BooleanField("Возможность выдавать задания", default=True)
    cpe_flag = models.BooleanField("Флаг ГИП (техническая метка)", default=False)

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.middle_name}'

    class Meta:
        verbose_name = _("сотрудник")
        verbose_name_plural = _("сотрудники")


class CanAcceptModel(models.Model):
    """Таблица тех, кому могут назначаться задания"""
    dep_accept = models.ForeignKey(CommandNumberModel, on_delete=models.PROTECT, verbose_name="Отдел за который можно подписаться", null=True)
    user_accept = models.ForeignKey(Employee, on_delete=models.PROTECT, verbose_name="Сотрудник", null=True)

    def __str__(self):
        return f'{self.dep_accept.command_number}, {self.user_accept} ({self.user_accept.job_title.job_title})'

    class Meta:
        verbose_name = _("принимающий задания")
        verbose_name_plural = _("принимающие задания")


class OrdersModel(models.Model):
    """    Таблица номеров заказов    """
    order = models.IntegerField("Номер заказа")

    class Meta:
        verbose_name = _("номер заказа")
        verbose_name_plural = _("номера заказов")

    def __str__(self):
        return f'{self.order}'


class ObjectModel(models.Model):
    """Таблица с наименованиями объектов"""
    object_name = models.CharField("Наименование объекта", max_length=250, default=None)

    class Meta:
        verbose_name = _("наименование объекта")
        verbose_name_plural = _("наименования объектов")

    def __str__(self):
        return f'{self.object_name}'


class ContractModel(models.Model):
    """Таблица договоров"""
    contract_object = models.ForeignKey(ObjectModel, on_delete=models.PROTECT, verbose_name="Номер договора", default=1)
    contract_name = models.CharField(max_length=250, verbose_name="Номер договора")

    class Meta:
        verbose_name = _("номер договора")
        verbose_name_plural = _("номера договоров")

    def __str__(self):
        return f'{self.contract_object}, {self.contract_name}'


class StageModel(models.Model):
    """Таблица этапов"""
    stage_contract = models.ForeignKey(ContractModel, on_delete=models.PROTECT, verbose_name="Номер договора")
    stage_name = models.CharField(max_length=250, verbose_name="Наименование этапа")

    class Meta:
        verbose_name = _("наименование этапа")
        verbose_name_plural = _("наименования этапов")

    def __str__(self):
        return f'{self.stage_contract.contract_object}, {self.stage_contract}, {self.stage_name}'


class CpeModel(models.Model):
    """Таблица ГИП-ов"""
    cpe_user = models.ForeignKey(Employee, on_delete=models.SET_NULL, verbose_name="Сотрудник", null=True)
    cpe_object = models.ForeignKey(ObjectModel, on_delete=models.PROTECT, verbose_name="Объект", null=True)

    class Meta:
        verbose_name = _("ГИП")
        verbose_name_plural = _("ГИПЫ")

    def __str__(self):
        return f'{self.cpe_user}, {self.cpe_object}'


class TaskModel(models.Model):
    """    Таблица заданий    """

    class StatusTaskChoice(models.IntegerChoices):
        """        Статус задания       """
        ON_SIGN = 1, _('На подписании')
        ACTUAL = 2, _('Актуально')
        CORRECTION = 3, _('На корректировке')
        CANCELED = 0, _('Аннулировано')

    class TypeWorkTask(models.IntegerChoices):
        """        Выбор вида документации        """
        WD = 0, _('Не указан')
        RD = 1, _('РД')
        PD = 2, _('ПД')

    author = models.ForeignKey(Employee, on_delete=models.PROTECT, verbose_name="Автор задания")
    text_task = models.TextField("Текст задания", max_length=5000)
    task_number = models.CharField("Номер задания", max_length=15)
    department_number = models.ForeignKey(CommandNumberModel, verbose_name="Номер отдела", on_delete=models.PROTECT,
                                          null=True)
    task_type_work = models.IntegerField("Вид документации:", choices=TypeWorkTask.choices, default=0)
    task_order = models.ForeignKey(OrdersModel, on_delete=models.PROTECT, verbose_name="Номер заказа")
    task_object = models.ForeignKey(ObjectModel, on_delete=models.PROTECT, verbose_name="Наименование объекта")
    task_contract = models.ForeignKey(ContractModel, on_delete=models.PROTECT, verbose_name="Номер контракта")
    task_stage = models.ForeignKey(StageModel, on_delete=models.PROTECT, verbose_name="Этап договора")
    task_building = models.CharField("Здание", max_length=150, null=True)
    task_change_number = models.IntegerField("Номер изменения", default=0, null=True)
    first_sign_user = models.ForeignKey(Employee, on_delete=models.PROTECT, null=True,
                                        verbose_name="Первый руководитель", related_name="first_sign_user_employee")
    first_sign_status = models.BooleanField("Подпись первого руководителя", default=False)
    first_sign_date = models.DateTimeField("Дата и время подписи первого подписанта", default=None,
                                           null=True)
    second_sign_user = models.ForeignKey(Employee, on_delete=models.PROTECT, null=True,
                                         verbose_name="Второй руководитель", related_name="second_sign_user_employee")
    second_sign_status = models.BooleanField("Подпись второго руководителя", default=False)
    second_sign_date = models.DateTimeField("Дата и время подписи первого подписанта", default=None,
                                            null=True)
    cpe_sign_user = models.ForeignKey(Employee, on_delete=models.PROTECT, null=True,
                                      verbose_name="Главный инженер проекта", related_name="cpe_sign_user_employee")
    cpe_sign_date = models.DateTimeField("Дата и время подписи первого подписанта", default=None, null=True)
    cpe_sign_status = models.BooleanField("Подпись ГИП-а", default=False)
    cpe_comment = models.TextField("Текст задания", max_length=5000, null=True, default=None)
    back_to_change = models.BooleanField("Возвращено на доработку", default=False)
    task_status = models.IntegerField("Статус задания", choices=StatusTaskChoice.choices,
                                      default=StatusTaskChoice.ON_SIGN)
    task_create_date = models.DateTimeField("Дата создания", auto_now_add=True, null=True)
    task_last_edit = models.DateTimeField("Дата последнего изменения", null=True)
    incoming_dep = models.ForeignKey(CommandNumberModel, on_delete=models.SET_NULL, null=True,
                                     verbose_name="Отдел принимающий задание", related_name="incoming_dep_id")
    incoming_employee = models.ForeignKey(Employee, verbose_name="Кто принял",
                                          on_delete=models.SET_NULL, null=True, related_name="incoming_emp_id")
    incoming_status = models.BooleanField("Принимающий принял задание", default=False)
    incoming_date = models.DateTimeField("Дата и время подписи принявшего", default=None,
                                         null=True)
    task_workers = models.BooleanField("Наличие исполнителей", default=False)
    task_approved = models.BooleanField("Согласовано", default=False)
    task_need_approve = models.BooleanField("Требуются ли согласователи?", default=False)


    def __str__(self):
        return f'{self.task_number}, {self.task_order}, {self.task_object}, {self.task_contract}'

    class Meta:
        verbose_name = _("задание")
        verbose_name_plural = _("задания")


class TaskNumbersModel(models.Model):
    """Номера заданий под отделам"""

    command_number = models.ForeignKey(CommandNumberModel, on_delete=models.PROTECT)
    year_of_task = models.IntegerField("Год выдачи заданий", default=datetime.datetime.today().year)
    count_of_task = models.IntegerField("Счетчик заданий", default=1)

    def __str__(self):
        return f'Отдел {self.command_number} в {self.year_of_task} году выдал {self.count_of_task}'

    class Meta:
        verbose_name = _("счетчик заданий")
        verbose_name_plural = _("счетчики заданий")


class WorkerModel(models.Model):
    """Таблица назначенных исполнителей"""

    worker_user = models.ForeignKey(Employee, on_delete=models.SET_NULL, verbose_name="Сотрудник", null=True)
    task = models.ForeignKey(TaskModel, on_delete=models.CASCADE, verbose_name="Задание", null=True)
    # comment = models.CharField("Комментарий", max_length=200, null=True)
    read_status = models.BooleanField("Статус прочтения", default=False)

    class Meta:
        verbose_name = _("ответственный исполнитель")
        verbose_name_plural = _("ответственные исполнители")


class ApproveModel(models.Model):
    """Таблица согласователей"""

    approve_user = models.ForeignKey(Employee, on_delete=models.SET_NULL, verbose_name="Согласователь", null=True, blank=True)
    approve_task = models.ForeignKey(TaskModel, on_delete=models.CASCADE, verbose_name="Задание", null=True)
    approve_status = models.BooleanField("Статус подписи", default=False)
    approve_date = models.DateTimeField("Дата подписания", default=None, null=True)


class BackCommentModel(models.Model):
    """Таблица заданий возвраты"""
    task = models.ForeignKey(TaskModel, on_delete=models.CASCADE, verbose_name="Задание", null=True)
    bad_comment = models.TextField("Текст задания", max_length=5000, null=True, default=None)
