from django import forms
from todo.models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'complete']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Enter task title',
                'class': 'form-input',
                'required': True,
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Enter task description (optional)',
                'rows': 4,
                'class': 'form-input',
            }),
            'complete': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
            }),
        }
        labels = {
            'title': 'Task Title',
            'description': 'Description',
            'complete': 'Mark as Completed',
        }
