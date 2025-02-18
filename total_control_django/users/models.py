from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Связь с встроенной моделью пользователя Django
    birth_date = models.DateField(null=True, blank=True)  # Дата рождения
    height = models.FloatField(null=True, blank=True)  # Рост (см)
    weight = models.FloatField(null=True, blank=True)  # Вес (кг)
    goal = models.CharField(
        max_length=50,
        choices=[
            ('lose_weight', 'Похудение'),
            ('gain_muscle', 'Набор массы'),
            ('maintain', 'Поддержание формы'),
            ('cutting', 'Сушка')
        ],
        default='maintain'
    )  # Цель
    daily_calories = models.FloatField(null=True, blank=True)  # Расчет нормы калорий
    daily_water = models.FloatField(null=True, blank=True)  # Расчет нормы воды (литры)

    def __str__(self):
        return self.user.username
