# Generated by Django 4.1.3 on 2022-11-18 22:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ToDo_tasks', '0023_alter_employee_department'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskmodel',
            name='incoming_date',
            field=models.DateTimeField(default=None, null=True, verbose_name='Дата и время подписи первого подписанта'),
        ),
        migrations.AddField(
            model_name='taskmodel',
            name='incoming_employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ToDo_tasks.canacceptmodel', verbose_name='Кто может принимает задание'),
        ),
        migrations.AddField(
            model_name='taskmodel',
            name='incoming_status',
            field=models.BooleanField(default=False, verbose_name='Принимающий принял задание'),
        ),
    ]
