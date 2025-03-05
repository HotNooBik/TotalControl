from django.contrib import admin
from . import models

# Register your models here.
@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user",
                    "birth_date", 
                    "sex", 
                    "height", 
                    "weight", 
                    "goal", 
                    "daily_calories", 
                    "daily_water", 
                    "daily_proteins",
                    "daily_fats", 
                    "daily_carbs")
