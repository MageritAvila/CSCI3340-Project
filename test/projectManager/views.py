import datetime

from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
# from django.http import HttpResponse

from .models import Project, Comment, Task

User = get_user_model()

def home(request):
	return render(request, 'home.html',{})

@login_required(login_url='login')
def dashboard(request, username):
    if request.user.username != username:
        return redirect('dashboard', username=request.user.username)

    projects = Project.objects.filter(creator=request.user)
    shared_projects = request.user.shared_projects.all()
    
    # Get all projects the user has access to
    user_projects = projects | shared_projects
    
    # Get all tasks that are overdue or due within a week from now
    one_week_from_now = timezone.now() + timedelta(days=7)
    upcoming_tasks_qs = Task.objects.filter(
        project__in=user_projects,
        due_date__lte=one_week_from_now
    ).order_by('due_date').distinct()
    
    # Build a list of tasks with their associated projects
    upcoming_tasks = []
    for task in upcoming_tasks_qs:
        task_projects = Project.objects.filter(tasks=task, id__in=user_projects)
        if task_projects.exists():
            # Use the first project (usually there's only one)
            upcoming_tasks.append({
                'task': task,
                'project_name': task_projects.first().name
            })
    
    return render(request, 'dashboard.html', {
        'username': username,
        'projects': projects,
        'shared_projects': shared_projects,
        'upcoming_tasks': upcoming_tasks,
    })

def login(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect("dashboard", username=username)
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html', {})

def logout(request):
    auth.logout(request)
    return redirect("home")

def signup(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        errors = []

        if not full_name:
            errors.append("Full name is required.")
        if not email:
            errors.append("Email is required.")
        if not username:
            errors.append("Username is required.")
        if not password:
            errors.append("Password is required.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if User.objects.filter(username=username).exists():
            errors.append("That username is already taken.")
        if User.objects.filter(email=email).exists():
            errors.append("That email is already registered.")

        if not errors:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=full_name,
            )
            user.save()

            messages.success(request, "Account created successfully. Please sign in.")
            return redirect("login")

        return render(request, "signup.html", {
            "errors": errors,
            "full_name": full_name,
            "email": email,
            "username": username,
        })

    return render(request, "signup.html", {})

@login_required(login_url='login')
def create_project(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()

        if not name:
            messages.error(request, "Project name is required.")
        else:
            Project.objects.create(
                name=name,
                description=description,
                creator=request.user
            )
            messages.success(request, f"Project '{name}' created successfully.")
            return redirect("dashboard", username=request.user.username)

    return render(request, "projectCreation.html", {})

@login_required(login_url='login')
def project_detail(request, project_id):
    project = Project.objects.get(id=project_id)

    if request.user != project.creator and request.user not in project.shared_with.all():
        messages.error(request, "You do not have access to this project.")
        return redirect('dashboard', username=request.user.username)

    if request.method == "POST":
        action = request.POST.get('action')

        if action == 'add_post':
            message = request.POST.get('message', '').strip()
            image_file = request.FILES.get('image', None)

            if not message and not image_file:
                messages.error(request, "Add a message or image before posting.")
            else:
                comment = Comment.objects.create(
                    user=request.user,
                    project=project,
                    content=message,
                )
                if image_file:
                    comment.image = image_file
                    comment.save()
                messages.success(request, "Board post added.")
                return redirect('project_detail', project_id=project.id)

        elif action == 'share_project':
            username = request.POST.get('share_username', '').strip()
            if not username:
                messages.error(request, "Enter a username to share with.")
            else:
                try:
                    target = User.objects.get(username=username)
                    if target == project.creator:
                        messages.error(request, "Project creator already has access.")
                    else:
                        project.shared_with.add(target)
                        messages.success(request, f"Project shared with {username}.")
                        return redirect('project_detail', project_id=project.id)
                except User.DoesNotExist:
                    messages.error(request, "That user does not exist.")

        elif action == 'add_task':
            task_name = request.POST.get('task_name', '').strip()
            task_description = request.POST.get('task_description', '').strip()
            due_date = request.POST.get('due_date', '').strip()
            max_assignees = request.POST.get('max_assignees', '1').strip()

            if not task_name:
                messages.error(request, "Task name is required.")
            else:
                try:
                    max_assignees = max(1, int(max_assignees))
                except ValueError:
                    max_assignees = 1

                if due_date:
                    try:
                        due = datetime.datetime.strptime(due_date, '%Y-%m-%d')
                    except ValueError:
                        due = timezone.now()
                else:
                    due = timezone.now()

                task = Task.objects.create(
                    name=task_name,
                    description=task_description,
                    due_date=due,
                    creator=request.user,
                    max_assignees=max_assignees,
                )
                project.tasks.add(task)
                messages.success(request, f"Task '{task_name}' added to the project.")
                return redirect('project_detail', project_id=project.id)

        elif action == 'claim_task':
            task_id = request.POST.get('task_id')
            if task_id:
                try:
                    task = Task.objects.get(id=task_id)
                    if task not in project.tasks.all():
                        messages.error(request, "This task does not belong to the current project.")
                    elif request.user in task.claimed_by.all():
                        messages.info(request, "You have already claimed this task.")
                    elif task.is_full:
                        messages.error(request, "This task already has the maximum number of assignees.")
                    else:
                        task.claimed_by.add(request.user)
                        messages.success(request, f"You claimed '{task.name}'.")
                        return redirect('project_detail', project_id=project.id)
                except Task.DoesNotExist:
                    messages.error(request, "Task not found.")
            else:
                messages.error(request, "Invalid task selection.")

        elif action == 'unclaim_task':
            task_id = request.POST.get('task_id')
            if task_id:
                try:
                    task = Task.objects.get(id=task_id)
                    if task not in project.tasks.all():
                        messages.error(request, "This task does not belong to the current project.")
                    elif request.user not in task.claimed_by.all():
                        messages.error(request, "You haven't claimed this task.")
                    else:
                        task.claimed_by.remove(request.user)
                        messages.success(request, f"You unclaimed '{task.name}'.")
                        return redirect('project_detail', project_id=project.id)
                except Task.DoesNotExist:
                    messages.error(request, "Task not found.")
            else:
                messages.error(request, "Invalid task selection.")

        elif action == 'toggle_task_done':
            task_id = request.POST.get('task_id')
            if task_id:
                try:
                    task = Task.objects.get(id=task_id)
                    if task not in project.tasks.all():
                        messages.error(request, "This task does not belong to the current project.")
                    elif request.user not in task.claimed_by.all() and request.user != project.creator:
                        messages.error(request, "Only users who claimed this task or the project creator can mark it complete.")
                    else:
                        task.is_complete = not task.is_complete
                        task.save()
                        status = 'completed' if task.is_complete else 'marked incomplete'
                        messages.success(request, f"Task '{task.name}' {status}.")
                        return redirect('project_detail', project_id=project.id)
                except Task.DoesNotExist:
                    messages.error(request, "Task not found.")
            else:
                messages.error(request, "Invalid task selection.")

    tasks = project.tasks.all()
    comments_raw = Comment.objects.filter(project=project).order_by('-timestamp')
    comments = []
    for comment in comments_raw:
        comments.append({
            'author': comment.user,
            'timestamp': comment.timestamp,
            'text': comment.content or '',
            'image': comment.image,
        })

    shared_users = project.shared_with.all()

    return render(request, 'projectDetails.html', {
        'project': project,
        'tasks': tasks,
        'comments': comments,
        'shared_users': shared_users,
    })

