# Generated by Django 4.1.3 on 2023-09-13 07:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ToDo_tasks', '0050_alter_taskmodel_task_type_work'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskmodel',
            name='task_type_work',
            field=models.IntegerField(choices=[(0, 'Не указан'), (1, 'РД'), (2, 'ПД')], default=0, verbose_name='Вид документации:'),
        ),
    ]