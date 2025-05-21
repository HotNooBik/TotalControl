from django.urls import path
from . import views

urlpatterns = [
    path("", views.calculator, name="calculator"),
    
    path("set-timezone/", views.set_timezone, name="set_timezone"),
    path("add-water/", views.add_water, name="add_water"),
    path("update-weight/", views.update_weight, name="update_weight"),
    path("get-weight-history/", views.get_weight_history_graph, name="get_weight_history"),
    path("get-records-history/", views.get_records_history_graph, name="get_records_history"),

    path("food-search/<str:meal>/", views.food_search, name="food_search"),
    path("own-food-search/<str:meal>/", views.own_food_search, name="own_food_search"),
    path("favorite-food-search/<str:meal>/", views.favorite_food_search, name="favorite_food_search"),

    path("add-food/<str:food_id>/", views.add_food_entry, name="add_food_entry"),
    path("add-fast-entry/", views.add_fast_entry, name="add_fast_entry"),
    path("delete/<int:entry_id>/", views.delete_entry, name="delete_entry"),

    path("create-food", views.create_custom_fodd, name="create_custom_food"),
    path("delete-food/<int:food_id>/", views.delete_custom_food, name="delete_custom_food"),
    path("edit-food/<int:food_id>/", views.edit_custom_food, name="edit_custom_food"),

    path("add-favorite/<str:food_id>/", views.add_food_to_favorites, name="add_food_to_favorites"),
    path("remove-favorite/<str:food_id>/", views.remove_food_from_favorites, name="remove_food_from_favorites"),

    path("food-recognition/", views.food_image_recognition, name="food_recognition"),
]
