from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.utils.translation import gettext_lazy as _


# Create your models here.
COMAND_CHOICES = [(000, "000 - Не указан"), (201, "201 - Строительный первый"), (202, "202 - Строительный второй")]

class Employee(models.Model):
    class GroupDepartment(models.IntegerChoices):
        UASP = 1, _("УАСП")
        USP = 2, _("УСП")


    user = models.OneToOneField(User, models.PROTECT, verbose_name="Пользователь")
    last_name = models.CharField("Фамилия", max_length=150)
    first_name = models.CharField("Имя", max_length=150)
    middle_name = models.CharField("Отчество", max_length=150)
    department = models.IntegerField("№ отдела", choices=COMAND_CHOICES, default=000)
    user_phone = models.IntegerField("№ телефона")
    department_group = models.IntegerField(verbose_name="Управление", default=None, choices=GroupDepartment.choices)
    check_edit = models.BooleanField("Возможность редактирования", default=False)

    def __str__(self):
        return f'{("%s %s" % (self.user.first_name, self.user.last_name)).strip()}'

    class Meta:
        verbose_name = _("сотрудник")
        verbose_name_plural = _("сотрудники")



class TaskModel(models.Model):
    class StatusTask(models.IntegerChoices):
        ACTIVE = 1, _('Активно')
        POSTPONED = 2, _('Отложено')
        DONE = 3, _('Выполнено')

    author = models.ForeignKey(Employee, on_delete=models.PROTECT, verbose_name="Автор задания")
    text_task = models.TextField("Текст задания", max_length=5000)
    task_number = models.CharField("Номер задания", max_length=10)
    department_number = models.IntegerField("Номер отдела", choices=COMAND_CHOICES, default=000)


    def __str__(self):
        return f'{self.task_number}'

    class Meta:
        verbose_name = _("задание")
        verbose_name_plural = _("задания")