from django.contrib import admin
from . import models


@admin.register(models.FoodEntry)
class FoodEntryAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "date_added",
        "food_name",
        "calories",
        "proteins",
        "fats",
        "carbs",
        "amount",
        "meal",
    )


@admin.register(models.UserCustomFood)
class UserCustomFoodAdmin(admin.ModelAdmin):
    list_display = (
        "food_id",
        "food_name",
        "brand_name",
        "serving_name",
        "calories",
        "proteins",
        "fats",
        "carbs",
        "calories_100g",
        "proteins_100g",
        "fats_100g",
        "carbs_100g",
        "calories_100ml",
        "proteins_100ml",
        "fats_100ml",
        "carbs_100ml",
        "created_at",
        "updated_at",
        "user_id",
    )


@admin.register(models.UserFavoriteCustomFood)
class UserFavoriteCustomFoodAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "food_id",
        "created_at",
    )


@admin.register(models.UserFavoriteApiFood)
class UserFavoriteApiFoodAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "food_id",
        "food_name",
        "brand_name",
        "food_description",
        "created_at",
    )
