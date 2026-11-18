from django.contrib import admin
from todo.models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'complete', 'date_of_creation', 'date_of_updation')
    list_filter = ('complete', 'date_of_creation', 'user')
    search_fields = ('title', 'description', 'user__username')
    list_editable = ('complete',)
