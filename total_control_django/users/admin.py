from django.contrib import admin
from . import models


# Register your models here.
@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "birth_date",
        "sex",
        "height",
        "weight",
        "goal",
        "activity_coef",
        "daily_calories",
        "daily_water",
        "daily_proteins",
        "daily_fats",
        "daily_carbs",
    )


@admin.register(models.UserDailyRecord)
class UserDailyRecordAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "user_date",
        "weight",
        "calories",
        "proteins",
        "fats",
        "carbs",
        "water",
    )
