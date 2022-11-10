# Generated by Django 4.1.3 on 2022-11-10 19:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ToDo_tasks', '0016_alter_taskmodel_task_type_work'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobTitleModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_title', models.CharField(max_length=200, verbose_name='Должность')),
            ],
            options={
                'verbose_name': 'должность',
                'verbose_name_plural': 'должности',
            },
        ),
        migrations.RenameField(
            model_name='taskmodel',
            old_name='taas_change_number',
            new_name='task_change_number',
        ),
        migrations.AddField(
            model_name='employee',
            name='right_to_sign',
            field=models.BooleanField(default=False, verbose_name='Право подписывать'),
        ),
        migrations.AddField(
            model_name='taskmodel',
            name='back_to_change',
            field=models.BooleanField(default=False, verbose_name='Возвращено на доработку'),
        ),
        migrations.AddField(
            model_name='taskmodel',
            name='cpe_sign',
            field=models.BooleanField(default=False, verbose_name='Подпись ГИП-а'),
        ),
        migrations.AddField(
            model_name='taskmodel',
            name='cpe_sign_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='cpe_sign_user_employee', to='ToDo_tasks.employee', verbose_name='Главный инженер проекта'),
        ),
        migrations.AddField(
            model_name='taskmodel',
            name='first_sign_status',
            field=models.BooleanField(default=False, verbose_name='Подпись первого руководителя'),
        ),
        migrations.AddField(
            model_name='taskmodel',
            name='first_sign_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='first_sign_user_employee', to='ToDo_tasks.employee', verbose_name='Первый руководитель'),
        ),
        migrations.AddField(
            model_name='taskmodel',
            name='second_sign',
            field=models.BooleanField(default=False, verbose_name='Подпись второго руководителя'),
        ),
        migrations.AddField(
            model_name='taskmodel',
            name='second_sign_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='second_sign_user_employee', to='ToDo_tasks.employee', verbose_name='Второй руководитель'),
        ),
        migrations.AlterField(
            model_name='taskmodel',
            name='task_type_work',
            field=models.IntegerField(choices=[(0, 'Не указан'), (1, 'РД'), (2, 'ПД')], default=0, verbose_name='Вид документации:'),
        ),
        migrations.AddField(
            model_name='employee',
            name='job_title',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='ToDo_tasks.jobtitlemodel', verbose_name='Должность'),
        ),
    ]
