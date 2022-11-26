from django.urls import path
from . import views
from django.contrib.auth.views import PasswordChangeView

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('my_outgoing_tasks/', views.UserTaskView.as_view(), name='my_tasks'),
    path('inbox', views.MyInboxListView.as_view(), name='inbox'),
    path('my_tasks_on_sign/', views.UserTaskOnSignView.as_view(), name='my_tasks_on_sign'),
    path('add_task/', views.AddTaskView.as_view(), name='add_task'),
    # path('add_task/<int:pk>', views.AddTaskView.as_view(), name='add_task'),  # просмотр добавленного задания
    path('add_task_change/<int:pk>', views.AddChangeTaskView.as_view(), name='add_task_change'),
    path('issued_tasks/', views.IssuedTasksView.as_view(), name="issued_tasks"),
    path('outgoing_tasks/', views.OutgoingTasksView.as_view(), name="outgoing_tasks"),
    path('details/<int:pk>', views.DetailView.as_view(), name='details'),
    path('ajax/load-contracts/', views.load_contracts, name='ajax_load_contracts'),
    path('ajax/load-stages/', views.load_stages, name='ajax_load_stages'),
    path('ajax/inc_emp/', views.load_incoming_employee, name='ajax_load_inc_emp'),
    path('change_password/', PasswordChangeView.as_view(
        template_name='todo_tasks/system_user/change_password.html',
        success_url='/'), name='change_password'),
    path('details/<int:pk>/change', views.EditTaskView.as_view(), name='change'),
    path('details_to_sign/<int:pk>', views.ToSignDetailView.as_view(), name='details_to_sign'),
    path('details_to_add_workers/<int:pk>', views.ToAddWorkersDetailView.as_view(), name='details_to_add_workers'),
    path('outgoing_to_sign/', views.ToSignListView.as_view(), name='outgoing_to_sign'),
    path("incoming_to_dep/", views.IncomingDepView.as_view(), name='incoming_to_dep'),
    path("incoming_to_sign/", views.IncomingListView.as_view(), name='incoming_to_sign'),
    path("incoming_to_sign_details/<int:pk>", views.IncomingSignDetails.as_view(), name='incoming_to_sign_details'),
    path('incoming_to_workers/', views.ToWorkerListView.as_view(), name='incoming_to_workers'),
    path('search_result/<str:pk>', views.SearchView.as_view(), name='search_result'),
    path('advanced_search/', views.AdvancedSearchView.as_view(), name='advanced_search'),
    path('temp_to_read_task/<int:pk>', views.MyInboxReadTask.as_view(), name='read_task'),
    path('temp_to_delete_worker/<int:pk>', views.ToAddWorkersDetailView.as_view(), name='delete_worker'),
    path('edit_workers/', views.EditWorkerListView.as_view(), name='edit_workers')


]
