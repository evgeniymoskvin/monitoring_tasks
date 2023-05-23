# Generated by Django 4.1.3 on 2023-05-22 19:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ToDo_tasks', '0041_alter_approvemodel_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='FavoritesListModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('favorite_list_name', models.CharField(max_length=25, verbose_name='Название списка')),
            ],
            options={
                'verbose_name': 'список избранного',
                'verbose_name_plural': 'списки избранных',
            },
        ),
        migrations.AddField(
            model_name='employee',
            name='work_status',
            field=models.BooleanField(default=True, verbose_name='Сотрудник работает'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='user_phone',
            field=models.IntegerField(default=None, null=True, verbose_name='№ телефона'),
        ),
        migrations.CreateModel(
            name='TasksInFavoritesModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('favorite_list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ToDo_tasks.favoriteslistmodel', verbose_name='Список избранного')),
                ('favorite_task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ToDo_tasks.taskmodel', verbose_name='Задание')),
            ],
            options={
                'verbose_name': 'задание в избранном',
                'verbose_name_plural': 'задания в избранном',
            },
        ),
        migrations.CreateModel(
            name='FavoritesShareModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('can_change_list', models.BooleanField(blank=True, default=False, verbose_name='Право редактировать список')),
                ('favorite_list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ToDo_tasks.favoriteslistmodel', verbose_name='Список избранного')),
                ('favorite_share_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ToDo_tasks.employee', verbose_name='Доверенный пользователь')),
            ],
            options={
                'verbose_name': 'расшаренный пользователь избранного',
                'verbose_name_plural': 'расшаренные пользователи избранного',
            },
        ),
        migrations.AddField(
            model_name='favoriteslistmodel',
            name='favorite_list_holder',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ToDo_tasks.employee', verbose_name='Владелец списка'),
        ),
    ]
