# Generated by Django 4.1.3 on 2022-11-03 18:19

import django.contrib.auth.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ToDo_tasks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='user_first_name',
            field=models.CharField(default=0, editable=False, max_length=150, verbose_name=django.contrib.auth.models.User),
            preserve_default=False,
        ),
    ]
