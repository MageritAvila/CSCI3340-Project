from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
import uuid


class Task(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    shared_with = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='shared_tasks')
    claimed_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='claimed_tasks', blank=True)
    max_assignees = models.PositiveIntegerField(default=1)
    is_complete = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    def is_overdue(self):
        return timezone.now() > self.due_date

    def is_due_soon(self):
        now = timezone.now()
        return now <= self.due_date <= now + datetime.timedelta(days=3)

    def claimed_count(self):
        return self.claimed_by.count()

    @property
    def is_full(self):
        return self.claimed_by.count() >= self.max_assignees

class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    shared_with = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='shared_projects')
    tasks = models.ManyToManyField(Task)
    def __str__(self):
        return self.name

class User(AbstractUser):
    projects = models.ManyToManyField(Project)
    UID = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    def __str__(self):
        return self.username

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # The commenter
    project = models.ForeignKey(Project, on_delete=models.CASCADE)  # Always set
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)  # Optional, for task-specific comments
    content = models.TextField()
    image = models.ImageField(upload_to='comments/', null=True, blank=True)  # Uploaded image
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.task:
            return f"{self.user.username} on task {self.task.name} (project {self.project.name})"
        else:
            return f"{self.user.username} on project {self.project.name}"
    
    def was_recently_posted(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.timestamp <= now
    
    def clean(self):
        if self.task and self.task.project != self.project:
            raise ValidationError("If commenting on a task, the project must match the task's project.")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
