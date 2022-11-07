from .models import TaskModel
from django.forms import ModelForm, TextInput, Textarea, CheckboxInput, Select

class TaskForm(ModelForm):
    class Meta:
        model = TaskModel
        # fields = '__all__'
        exclude = ["author", 'department_number', 'task_number']
        widgets = {"text_task": Textarea(attrs={"placeholder": "Введите текст",
                                              "class": "form-control"}),
                   "task_type_work": Select(attrs={"class": "form-select",
                                                   "aria-label": "Вид документации"})
                   }