# Generated by Django 4.1.3 on 2022-11-07 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ToDo_tasks', '0009_alter_taskmodel_author_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskmodel',
            name='task_type_work',
            field=models.IntegerField(choices=[(1, 'РД'), (2, 'ПД'), (3, 'Не указан')], default=3, verbose_name='Вид документации:'),
        ),
    ]
