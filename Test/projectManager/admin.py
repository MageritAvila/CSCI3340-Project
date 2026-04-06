from django.contrib import admin

from .models import Task, Project, User, Comment

# Register your models here.
admin.site.register(Task)
admin.site.register(Project)
admin.site.register(User)
admin.site.register(Comment)
