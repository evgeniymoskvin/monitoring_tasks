from django.contrib import admin
from .models import TaskModel, Employee, OrdersModel, ObjectModel, ContractModel, StageModel, JobTitleModel, CpeModel, \
    CanAcceptModel, CommandNumberModel, TaskNumbersModel, GroupDepartmentModel, MarkDocModel, WorkerModel, \
    BackCommentModel, ApproveModel, FavoritesListModel, TasksInFavoritesModel, FavoritesShareModel, CanChangeWorkersModel, DraftTaskModel, ConnectionTaskModel


class TaskAdmin(admin.ModelAdmin):
    # list_display = ("author", "text_task")
    search_fields = ["author", "task_number", "permission_number", "task_building"]
    list_filter = ('department_number', "author", )
    ordering = ["id"]


class EmployeeAdmin(admin.ModelAdmin):
    # list_display = ("author", "text_task")
    ordering = ["last_name"]
    search_fields = ["user"]
    # list_filter = ("author", "task_number")


class ContractAdmin(admin.ModelAdmin):
    list_filter = ("contract_object",)


class StageAdmin(admin.ModelAdmin):
    list_filter = ("stage_contract__contract_object",)


class MarkDocAdmin(admin.ModelAdmin):
    ordering = ["mark_doc"]


class CommandNumberAdmin(admin.ModelAdmin):
    ordering = ["command_number"]


class CpeAdmin(admin.ModelAdmin):
    list_filter = ('cpe_object',)
    ordering = ["cpe_object"]
    search_fields = ["cpe_user"]

class ObjectAdmin(admin.ModelAdmin):
    ordering = ['object_name']

class CanChangeWorkersAdmin(admin.ModelAdmin):
    ordering = ['dep_accept']


admin.site.register(TaskModel, TaskAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(OrdersModel)
admin.site.register(ObjectModel, ObjectAdmin)
admin.site.register(ContractModel, ContractAdmin)
admin.site.register(StageModel, StageAdmin)
admin.site.register(JobTitleModel)
admin.site.register(CpeModel, CpeAdmin)
admin.site.register(CanAcceptModel)
admin.site.register(CommandNumberModel, CommandNumberAdmin)
admin.site.register(TaskNumbersModel)
admin.site.register(GroupDepartmentModel)
admin.site.register(MarkDocModel, MarkDocAdmin)
admin.site.register(WorkerModel)
admin.site.register(BackCommentModel)
admin.site.register(ApproveModel)
admin.site.register(FavoritesListModel)
admin.site.register(TasksInFavoritesModel)
admin.site.register(FavoritesShareModel)
admin.site.register(CanChangeWorkersModel)
admin.site.register(DraftTaskModel)
admin.site.register(ConnectionTaskModel)