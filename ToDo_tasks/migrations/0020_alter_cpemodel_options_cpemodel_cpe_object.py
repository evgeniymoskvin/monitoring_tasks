# Generated by Django 4.1.3 on 2022-11-16 20:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ToDo_tasks', '0019_cpemodel_canacceptmodel'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cpemodel',
            options={'verbose_name': 'ГИП', 'verbose_name_plural': 'ГИПЫ'},
        ),
        migrations.AddField(
            model_name='cpemodel',
            name='cpe_object',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='ToDo_tasks.objectmodel', verbose_name='Объект'),
        ),
    ]
