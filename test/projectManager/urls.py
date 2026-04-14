from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name ='home'),
    path("dashboard/<str:username>/", views.dashboard, name="dashboard"),
    path("login/", views.login, name="login"),
    path("signup/", views.signup, name="signup"),
]

# urlpatterns = [
#    path("dashboard/<str:user_id>/", views.dashboard, name="dashboard"),
#]