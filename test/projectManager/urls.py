from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name ='home'),
    path("dashboard/<str:username>/", views.dashboard, name="dashboard"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("signup/", views.signup, name="signup"),
    path("create_project/", views.create_project, name="create_project"),
    path("project/<int:project_id>/", views.project_detail, name="project_detail"),
]

