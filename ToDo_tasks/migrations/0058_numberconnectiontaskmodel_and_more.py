# Generated by Django 4.1.3 on 2023-09-19 06:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ToDo_tasks', '0057_remove_connectiontaskmodel_original_task_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='NumberConnectionTaskModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(blank=True, default=0, null=True, verbose_name='Номер взаимосвязи:')),
            ],
            options={
                'verbose_name': 'порядковый номер взаимосвязи',
                'verbose_name_plural': 'порядковые номера взаимосвязи',
            },
        ),
        migrations.AlterField(
            model_name='connectiontaskmodel',
            name='number_connection',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='connection_number', to='ToDo_tasks.numberconnectiontaskmodel', verbose_name='id взаимосвязи'),
        ),
        migrations.AlterField(
            model_name='taskmodel',
            name='have_connection',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='have_connections_tasks', to='ToDo_tasks.numberconnectiontaskmodel'),
        ),
    ]
