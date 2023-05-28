# Generated by Django 4.1.3 on 2023-05-28 21:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ToDo_tasks', '0043_alter_favoriteslistmodel_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CanChangeWorkersModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dep_accept', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='ToDo_tasks.commandnumbermodel', verbose_name='Отдел за который можно менять исполнителей')),
                ('user_accept', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='ToDo_tasks.employee', verbose_name='Сотрудник')),
            ],
            options={
                'verbose_name': 'назначающий исполнителей',
                'verbose_name_plural': 'назначающие исполнителей',
            },
        ),
    ]