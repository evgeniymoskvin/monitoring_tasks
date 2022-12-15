# Generated by Django 4.1.3 on 2022-12-15 21:38

import ToDo_tasks.models
import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ToDo_tasks', '0036_alter_approvemodel_approve_user_attachmentfilesmodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupDepartmentModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_dep_abr', models.CharField(max_length=10, verbose_name='Сокращенное название управления')),
                ('group_dep_name', models.CharField(max_length=250, verbose_name='Полное название управления')),
            ],
        ),
        migrations.AlterField(
            model_name='attachmentfilesmodel',
            name='file',
            field=models.FileField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(), upload_to=ToDo_tasks.models.upload_to, verbose_name='Файл'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='department_group',
            field=models.IntegerField(choices=[(1, 'УАСП'), (2, 'УСП')], default=None, null=True, verbose_name='Управление'),
        ),
    ]
