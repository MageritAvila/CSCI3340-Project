from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("This will be the Project Manager index. Can be login/signup page or dashboard, not sure yet.")
# Create your views here.
