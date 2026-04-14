from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
# from django.http import HttpResponse

User = get_user_model()

def home(request):
	return render(request, 'home.html',{})

def dashboard(request, user_id):
	return render(request, 'dashboard.html',{'user_id': user_id})

def login(request):
	return render(request, 'login.html',{})

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