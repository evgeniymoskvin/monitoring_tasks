# Generated by Django 4.1.3 on 2023-09-05 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ToDo_tasks', '0047_alter_contractmodel_contract_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='commandnumbermodel',
            name='show',
            field=models.BooleanField(default=True, verbose_name='Отображать отдел'),
        ),
    ]