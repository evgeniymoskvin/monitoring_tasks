from django.contrib import admin
from .models import TaskModel, Employee, OrdersModel, ObjectModel, ContractModel, StageModel, JobTitleModel


class TaskAdmin(admin.ModelAdmin):
    # list_display = ("author", "text_task")
    search_fields = ["author", "task_number", "permission_number"]
    list_filter = ("author", "task_number")


class EmployeeAdmin(admin.ModelAdmin):
    # list_display = ("author", "text_task")

    search_fields = ["user"]
    # list_filter = ("author", "task_number")


class ContractAdmin(admin.ModelAdmin):
    list_filter = ("contract_object",)


class StageAdmin(admin.ModelAdmin):
    list_filter = ("stage_contract__contract_object",)


admin.site.register(TaskModel, TaskAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(OrdersModel)
admin.site.register(ObjectModel)
admin.site.register(ContractModel, ContractAdmin)
admin.site.register(StageModel, StageAdmin)
admin.site.register(JobTitleModel)