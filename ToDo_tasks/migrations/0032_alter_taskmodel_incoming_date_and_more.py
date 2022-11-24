# Generated by Django 4.1.3 on 2022-11-24 20:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ToDo_tasks', '0031_canacceptmodel_dep_accept_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskmodel',
            name='incoming_date',
            field=models.DateTimeField(default=None, null=True, verbose_name='Дата и время подписи принявшего'),
        ),
        migrations.AlterField(
            model_name='taskmodel',
            name='incoming_employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='incoming_emp_id', to='ToDo_tasks.employee', verbose_name='Кто принял'),
        ),
    ]