from django.contrib import admin
from .models import TaskModel, Employee, OrdersModel, ObjectModel, ContractModel, StageModel, JobTitleModel, CpeModel, \
    CanAcceptModel, CommandNumberModel, TaskNumbersModel, GroupDepartmentModel, MarkDocModel, WorkerModel, \
    BackCommentModel, ApproveModel, FavoritesListModel, TasksInFavoritesModel, FavoritesShareModel, \
    CanChangeWorkersModel, DraftTaskModel, ConnectionTaskModel, CityDepModel, MoreDetailsEmployeeModel


class TaskAdmin(admin.ModelAdmin):
    # list_display = ("author", "text_task")
    search_fields = ["author", "task_number", "permission_number", "task_building", "author__last_name",
                     "author__first_name", "author__second_name"]
    list_filter = ('department_number', "department_number__department",)
    ordering = ["id"]


class EmployeeAdmin(admin.ModelAdmin):
    # list_display = ("author", "text_task")
    ordering = ["last_name"]
    search_fields = ["last_name", "first_name", "middle_name"]
    # list_filter = ("author", "task_number")


class ContractAdmin(admin.ModelAdmin):
    ordering = ['contract_object__object_name', 'contract_name']
    list_filter = ("contract_object",)


class OrdersAdmin(admin.ModelAdmin):
    ordering = ["order"]


class StageAdmin(admin.ModelAdmin):
    ordering = ['stage_contract__contract_object__object_name', 'stage_contract__contract_object', 'stage_name']
    search_fields = ["stage_name"]
    list_filter = ("stage_contract__contract_object",)


class MarkDocAdmin(admin.ModelAdmin):
    ordering = ["mark_doc"]


class CommandNumberAdmin(admin.ModelAdmin):
    ordering = ["command_number"]
    list_filter = ("department__city_dep__city", "department__group_dep_abr", "show")

class CpeAdmin(admin.ModelAdmin):
    list_filter = ('cpe_object',)
    ordering = ["cpe_object"]
    search_fields = ["cpe_user"]


class ObjectAdmin(admin.ModelAdmin):
    ordering = ['object_name']


class JobTitleAdmin(admin.ModelAdmin):
    ordering = ['job_title']


class TaskNumberAdmin(admin.ModelAdmin):
    ordering = ['command_number', 'year_of_task']
    list_filter = ('year_of_task', "command_number__command_number")


class WorkerAdmin(admin.ModelAdmin):
    ordering = ['task', 'worker_user']
    search_fields = ["worker_user__last_name", "worker_user__first_name", "worker_user__middle_name", 'task__task_number']


class CanChangeWorkersAdmin(admin.ModelAdmin):
    ordering = ['dep_accept__command_number']
    list_filter = ("dep_accept__department__city_dep__city", "dep_accept__department__group_dep_abr", "dep_accept__command_number",)
    search_fields = ["dep_accept__command_number", "user_accept__last_name", "user_accept__first_name",
                     "user_accept__middle_name"]


class CanAcceptAdmin(admin.ModelAdmin):
    ordering = ['dep_accept']
    list_filter = ("dep_accept__department__city_dep__city", "dep_accept__department__group_dep_abr", "dep_accept__command_number",)
    search_fields = ["dep_accept__command_number", "user_accept__last_name", "user_accept__first_name",
                     "user_accept__middle_name"]


class FavoritesListAdmin(admin.ModelAdmin):
    ordering = ['favorite_list_name', 'favorite_list_holder']
    search_fields = ["favorite_list_name", "favorite_list_holder__last_name", "favorite_list_holder__first_name",
                     "favorite_list_holder__middle_name"]

class FavoritesShareAdmin(admin.ModelAdmin):
    ordering = ['favorite_list', 'favorite_share_user']


class ApproveModelAdmin(admin.ModelAdmin):
    ordering = ['-approve_date', 'approve_task__task_number', 'approve_user']
    list_filter = ("approve_status",)
    search_fields = ["approve_task__task_number", "approve_user__last_name", "approve_user__first_name",
                     "approve_user__middle_name"]

class DraftTaskAdmin(admin.ModelAdmin):
    ordering = ['-draft_create_date']

class BackCommentAdmin(admin.ModelAdmin):
    ordering = ['-id']
    search_fields = ["task__task_number"]

class GroupDepartmentAdmin(admin.ModelAdmin):
    ordering = ['group_dep_abr', ]
    list_filter = ("city_dep__city", "show")

class MoreDetailsEmployeeAdmin(admin.ModelAdmin):
    ordering = ["emp__last_name", "emp__first_name", "emp__middle_name"]
    search_fields = ["emp__last_name", "emp__first_name", "emp__middle_name"]
    list_filter = ("emp__department_group__city_dep__city", "emp__department_group__group_dep_abr", "emp__department__command_number")


admin.site.register(TaskModel, TaskAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(OrdersModel, OrdersAdmin)
admin.site.register(ObjectModel, ObjectAdmin)
admin.site.register(ContractModel, ContractAdmin)
admin.site.register(StageModel, StageAdmin)
admin.site.register(JobTitleModel, JobTitleAdmin)
admin.site.register(CpeModel, CpeAdmin)
admin.site.register(CanAcceptModel, CanAcceptAdmin)
admin.site.register(CommandNumberModel, CommandNumberAdmin)
admin.site.register(TaskNumbersModel, TaskNumberAdmin)
admin.site.register(GroupDepartmentModel, GroupDepartmentAdmin)
admin.site.register(MarkDocModel, MarkDocAdmin)
admin.site.register(WorkerModel, WorkerAdmin)
admin.site.register(BackCommentModel, BackCommentAdmin)
admin.site.register(ApproveModel, ApproveModelAdmin)
admin.site.register(FavoritesListModel, FavoritesListAdmin)
admin.site.register(TasksInFavoritesModel)
admin.site.register(FavoritesShareModel, FavoritesShareAdmin)
admin.site.register(CanChangeWorkersModel, CanChangeWorkersAdmin)
admin.site.register(DraftTaskModel)
admin.site.register(ConnectionTaskModel)
admin.site.register(CityDepModel)
admin.site.register(MoreDetailsEmployeeModel, MoreDetailsEmployeeAdmin)