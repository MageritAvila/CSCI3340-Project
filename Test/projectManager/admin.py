from django.contrib import admin
from .models import User, Project, Task, Comment

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'UID']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'creator']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'creator', 'due_date']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'task', 'timestamp']