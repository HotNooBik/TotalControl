from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()


class FoodEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_name = models.CharField(max_length=255)
    calories = models.IntegerField(null=True)
    proteins = models.FloatField(null=True)
    fats = models.FloatField(null=True)
    carbs = models.FloatField(null=True)
    amount = models.CharField(max_length=255)
    meal = models.CharField(
        max_length=9,
        choices=[
            ("breakfast", "Завтрак"),
            ("lunch", "Обед"),
            ("dinner", "Ужин"),
            ("snack", "Перекус"),
        ],
        default="snack",
    )
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.food_name} ({self.amount})"
