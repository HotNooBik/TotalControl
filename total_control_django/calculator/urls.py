from django.urls import path, include
from . import views

urlpatterns = [
    path("calculator", views.calculator, name="calculator"),
]
