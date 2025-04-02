from django.urls import path
from . import views

urlpatterns = [
    path("calculator/", views.calculator, name="calculator"),
    path("food-search/<str:meal>/", views.food_search, name="food_search"),
    path("add-food/<str:food_id>/", views.add_food_entry, name="add_food_entry"),
    path("add-own-food/", views.add_own_food_entry, name="add_own_food_entry"),
    path("delete/<int:entry_id>/", views.delete_entry, name="delete_entry"),
]
