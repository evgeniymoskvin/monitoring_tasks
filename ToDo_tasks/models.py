from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.utils.translation import gettext_lazy as _

COMAND_CHOICES = [(000, "000 - Не указан"), (201, "201 - Строительный первый"), (202, "202 - Строительный второй")]


class JobTitleModel(models.Model):
    """ Таблица должностей """

    job_title = models.CharField("Должность", max_length=200)

    class Meta:
        verbose_name = _("должность")
        verbose_name_plural = _("должности")

    def __str__(self):
        return f'{self.job_title}'


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
    department = models.IntegerField("№ отдела", choices=COMAND_CHOICES, default=000)
    user_phone = models.IntegerField("№ телефона")
    department_group = models.IntegerField(verbose_name="Управление", default=None, choices=GroupDepartment.choices)
    right_to_sign = models.BooleanField(verbose_name="Право подписывать", default=False)
    check_edit = models.BooleanField("Возможность редактирования", default=False)

    def __str__(self):
        return f'{("%s %s %s" % (self.last_name, self.first_name, self.middle_name)).strip()}'

    class Meta:
        verbose_name = _("сотрудник")
        verbose_name_plural = _("сотрудники")


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


class TaskModel(models.Model):
    """    Таблица заданий    """

    class StatusTask(models.IntegerChoices):
        """        Тест       """
        ACTIVE = 1, _('Активно')
        POSTPONED = 2, _('Отложено')
        DONE = 3, _('Выполнено')

    class TypeWorkTask(models.IntegerChoices):
        """        Выбор вида документации        """
        WD = 0, _('Не указан')
        RD = 1, _('РД')
        PD = 2, _('ПД')

    author = models.ForeignKey(Employee, on_delete=models.PROTECT, verbose_name="Автор задания")
    text_task = models.TextField("Текст задания", max_length=5000)
    task_number = models.CharField("Номер задания", max_length=10)
    department_number = models.IntegerField("Номер отдела", choices=COMAND_CHOICES, default=000)
    task_type_work = models.IntegerField("Вид документации:", choices=TypeWorkTask.choices, default=0)
    task_order = models.ForeignKey(OrdersModel, on_delete=models.PROTECT, verbose_name="Номер заказа")
    task_object = models.ForeignKey(ObjectModel, on_delete=models.PROTECT, verbose_name="Наименование объекта")
    task_contract = models.ForeignKey(ContractModel, on_delete=models.PROTECT, verbose_name="Номер контракта")
    task_stage = models.ForeignKey(StageModel, on_delete=models.PROTECT, verbose_name="Этап договора")
    task_change_number = models.IntegerField("Номер изменения", default=None, null=True)
    first_sign_user = models.ForeignKey(Employee, on_delete=models.PROTECT, null=True,
                                        verbose_name="Первый руководитель", related_name="first_sign_user_employee")
    first_sign_status = models.BooleanField("Подпись первого руководителя", default=False)
    second_sign_user = models.ForeignKey(Employee, on_delete=models.PROTECT, null=True,
                                         verbose_name="Второй руководитель", related_name="second_sign_user_employee")
    second_sign_status = models.BooleanField("Подпись второго руководителя", default=False)
    cpe_sign_user = models.ForeignKey(Employee, on_delete=models.PROTECT, null=True,
                                      verbose_name="Главный инженер проекта", related_name="cpe_sign_user_employee")
    cpe_sign_status = models.BooleanField("Подпись ГИП-а", default=False)
    back_to_change = models.BooleanField("Возвращено на доработку", default=False)

    def __str__(self):
        return f'{self.task_number}, {self.author}'

    class Meta:
        verbose_name = _("задание")
        verbose_name_plural = _("задания")
