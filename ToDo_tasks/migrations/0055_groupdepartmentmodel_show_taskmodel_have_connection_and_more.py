# Generated by Django 4.1.3 on 2023-10-12 08:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ToDo_tasks', '0054_alter_drafttaskmodel_draft_building_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupdepartmentmodel',
            name='show',
            field=models.BooleanField(default=True, verbose_name='Отображать отдел'),
        ),
        migrations.AddField(
            model_name='taskmodel',
            name='have_connection',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Номер взаимосвязи с другими заданиями'),
        ),
        migrations.CreateModel(
            name='ConnectionTaskModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number_connection', models.IntegerField(blank=True, default=0, null=True, verbose_name='Номер взаимосвязи:')),
                ('dependent_task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='second_dependent_task', to='ToDo_tasks.taskmodel', verbose_name='Зависимое задание')),
            ],
            options={
                'verbose_name': 'взаимосвязь задания',
                'verbose_name_plural': 'взаимосвязи заданий',
            },
        ),
    ]