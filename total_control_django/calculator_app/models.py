from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()

class FoodEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_name = models.CharField(max_length=255)
    calories = models.IntegerField()
    proteins = models.IntegerField()
    fats = models.IntegerField()
    carbs = models.IntegerField()
    grams = models.IntegerField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.food_name} ({self.grams}g)"
