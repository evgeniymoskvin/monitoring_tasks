# Generated by Django 4.1.3 on 2022-11-08 17:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ToDo_tasks', '0013_contractmodel_objectmodel_stagemodel_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskmodel',
            name='task_contract',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='ToDo_tasks.contractmodel', verbose_name='Номер контракта'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='taskmodel',
            name='task_object',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='ToDo_tasks.objectmodel', verbose_name='Наименование объекта'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='taskmodel',
            name='task_stage',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='ToDo_tasks.stagemodel', verbose_name='Этап договора'),
            preserve_default=False,
        ),
    ]
