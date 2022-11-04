from django.contrib import admin
from .models import TaskModel, Employee


class TaskAdmin(admin.ModelAdmin):
    # list_display = ("author", "text_task")
    search_fields = ["author", "task_number", "permission_number"]
    list_filter = ("author", "task_number")

class EmployeeAdmin(admin.ModelAdmin):
    # list_display = ("author", "text_task")

    search_fields = ["user"]
    # list_display = ["author", "phone_number"]
    # list_filter = ("author", "task_number")

admin.site.register(TaskModel, TaskAdmin)
admin.site.register(Employee, EmployeeAdmin)

# Register your models here.
