# Generated by Django 4.1.3 on 2022-12-18 19:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ToDo_tasks', '0039_markdocmodel_alter_groupdepartmentmodel_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskmodel',
            name='task_contract',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='ToDo_tasks.contractmodel', verbose_name='Номер контракта'),
        ),
        migrations.AlterField(
            model_name='taskmodel',
            name='task_order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='ToDo_tasks.ordersmodel', verbose_name='Номер заказа'),
        ),
        migrations.AlterField(
            model_name='taskmodel',
            name='task_stage',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='ToDo_tasks.stagemodel', verbose_name='Этап договора'),
        ),
        migrations.AlterField(
            model_name='tasknumbersmodel',
            name='count_of_task',
            field=models.IntegerField(default=0, verbose_name='Счетчик заданий'),
        ),
    ]