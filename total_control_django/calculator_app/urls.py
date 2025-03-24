from django.urls import path
from . import views

urlpatterns = [
    path("calculator", views.calculator, name="calculator"),
    path('delete/<int:entry_id>/', views.delete_entry, name='delete_entry'),
]
