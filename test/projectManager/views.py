from django.shortcuts import render
# from django.http import HttpResponse

def home(request):
	return render(request, 'home.html',{})


# def index(request):
#    return HttpResponse("This will be the Project Manager index. Can be login/signup page with link to dashboard.")

#def dashboard(request):
#    return HttpResponse("This will be the Project Manager dashboard, showing projects and tasks.")