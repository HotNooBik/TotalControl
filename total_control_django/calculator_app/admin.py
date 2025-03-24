from django.contrib import admin
from . import models

@admin.register(models.FoodEntry)
class FoodEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_added', 'food_name', 'calories', 'proteins', 'fats', 'carbs', 'grams')
