from django.shortcuts import render
# from django.http import HttpResponse

def home(request):
	return render(request, 'home.html',{})

def dashboard(request, user_id):
	return render(request, 'dashboard.html',{'user_id': user_id})

def login(request):
	return render(request, 'login.html',{})

def signup(request):
	return render(request, 'signup.html',{})