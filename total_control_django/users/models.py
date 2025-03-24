from django.contrib.auth.models import User
from django.db import models



class UserProfile(models.Model):
    """
    Таблица пользователя со следующими полями:

    - user - индивидуальный айди пользователя, связанный с айда пользователей сайта (User)
    - birth_date - дата рождения
    - sex - пол (мужской, женский)
    - height - рост в сантиметрах
    - weight - вес в килограммах
    - goal - цель (похудеть, набор массы, поддержание формы, сушка)
    - activity_coef - коэффициент активности
    - daily_calories - дневная норма калорий
    - daily_water - дневная норма воды
    - daily_proteins - дневная норма белков
    - daily_fats - дневная норма жиров
    - daily_carbs - дневная норма углеводов
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateField(null=True, blank=True)
    sex = models.CharField(
        max_length=5,
        choices=[
            ('man', 'Мужской'),
            ('woman', 'Женский')
        ],
        default='man'
    )
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    goal = models.CharField(
        max_length=50,
        choices=[
            ('lose_weight', 'Похудение'),
            ('gain_muscle', 'Набор массы'),
            ('maintain', 'Поддержание формы'),
            ('cutting', 'Сушка')
        ],
        default='maintain'
    )
    activity_coef = models.FloatField(null=True, blank=True)
    daily_calories = models.IntegerField(null=True, blank=True)
    daily_water = models.IntegerField(null=True, blank=True)
    daily_proteins = models.IntegerField(null=True, blank=True)
    daily_fats = models.IntegerField(null=True, blank=True)
    daily_carbs = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Профиль пользователя {self.user.username}"
