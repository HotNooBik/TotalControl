from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_food, name='food_search'),
]