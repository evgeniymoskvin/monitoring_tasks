# Generated by Django 4.1.3 on 2022-11-28 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ToDo_tasks', '0034_taskmodel_task_approved'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskmodel',
            name='task_need_approve',
            field=models.BooleanField(default=False, verbose_name='Требуются ли согласователи?'),
        ),
    ]
