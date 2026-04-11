from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name ='home'),
]

# urlpatterns = [
#    path("", views.index, name="index"),
#    path("dashboard/<str:user_id>/", views.dashboard, name="dashboard"),
#]