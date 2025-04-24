from django.urls import path
from . import views

urlpatterns = [
    path("set-timezone/", views.set_timezone, name="set_timezone"),
    path("calculator/", views.calculator, name="calculator"),
    path("food-search/<str:meal>/", views.food_search, name="food_search"),
    path("own-food-search/<str:meal>/", views.own_food_search, name="own_food_search"),
    path("add-food/<str:food_id>/", views.add_food_entry, name="add_food_entry"),
    path("add-own-food/", views.add_own_food_entry, name="add_own_food_entry"),
    path("delete/<int:entry_id>/", views.delete_entry, name="delete_entry"),
    path("create-food", views.create_custom_fodd, name="create_custom_food"),
    path("delete-food/<int:food_id>/", views.delete_custom_food, name="delete_custom_food"),
    path("edit-food/<int:food_id>/", views.edit_custom_food, name="edit_custom_food"),
]
