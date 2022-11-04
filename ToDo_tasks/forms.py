from .models import TaskModel
from django.forms import ModelForm, TextInput, Textarea, CheckboxInput, Select

class TaskForm(ModelForm):
    class Meta:
        model = TaskModel
        exclude = ["author", 'department_number', 'task_number']
        widgets = {"text_task": Textarea(attrs={"placeholder": "Введите текст",
                                              "class": "form-control"}),
                   }