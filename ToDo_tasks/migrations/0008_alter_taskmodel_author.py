# Generated by Django 4.1.3 on 2022-11-03 20:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ToDo_tasks', '0007_alter_employee_department'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskmodel',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ToDo_tasks.employee'),
        ),
    ]
