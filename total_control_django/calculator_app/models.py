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


class UserCustomFood(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_id = models.AutoField(primary_key=True)
    food_name = models.CharField(max_length=100)
    brand_name = models.CharField(max_length=100, null=True, blank=True)
    serving_name = models.CharField(max_length=100)

    calories = models.IntegerField()
    proteins = models.FloatField()
    fats = models.FloatField()
    carbs = models.FloatField()

    calories_100g = models.IntegerField(null=True, blank=True)
    proteins_100g = models.FloatField(null=True, blank=True)
    fats_100g = models.FloatField(null=True, blank=True)
    carbs_100g = models.FloatField(null=True, blank=True)

    calories_100ml = models.IntegerField(null=True, blank=True)
    proteins_100ml = models.FloatField(null=True, blank=True)
    fats_100ml = models.FloatField(null=True, blank=True)
    carbs_100ml = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def to_api_format(self):
        """Преобразует объект в нужный формат"""
        return {
            "food_id": "ucf" + str(self.food_id),
            "food_name": self.food_name,
            "serving_name": self.serving_name,
            "brand_name": self.brand_name,
            "image": None,
            "per_portion": {
                "calories": self.calories,
                "proteins": self.proteins,
                "fats": self.fats,
                "carbs": self.carbs,
            },
            "per_100g": (
                {
                    "calories": self.calories_100g,
                    "proteins": self.proteins_100g,
                    "fats": self.fats_100g,
                    "carbs": self.carbs_100g,
                }
                if any(
                    [
                        self.calories_100g,
                        self.proteins_100g,
                        self.fats_100g,
                        self.carbs_100g,
                    ]
                )
                else None
            ),
            "per_100ml": (
                {
                    "calories": self.calories_100ml,
                    "proteins": self.proteins_100ml,
                    "fats": self.fats_100ml,
                    "carbs": self.carbs_100ml,
                }
                if any(
                    [
                        self.calories_100ml,
                        self.proteins_100ml,
                        self.fats_100ml,
                        self.carbs_100ml,
                    ]
                )
                else None
            ),
        }

    @classmethod
    def get_food_details(cls, user, food_id):
        try:
            food = cls.objects.get(user=user, food_id=food_id)
            return food.to_api_format()
        except cls.DoesNotExist:
            return None


class UserFavoriteCustomFood(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    custom_food = models.ForeignKey(UserCustomFood, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserFavoriteApiFood(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_id = models.IntegerField()
    food_name = models.CharField(max_length=100)
    brand_name = models.CharField(max_length=100, null=True, blank=True)
    food_description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
