from django.contrib.auth.models import User
from django.db import models

from .utils.nutrition_calculator import (
    get_user_calories_norm,
    get_user_pfc_norm,
    get_user_water_norm,
)


class UserProfile(models.Model):
    """Модель профиля пользователя с фитнес-метриками и целями.

    Содержит персональные данные пользователя, его физические параметры,
    цели и рассчитанные дневные нормы питательных веществ.

    Attributes:
        user (OneToOneField): Связь с моделью User (один к одному).
        birth_date (DateField): Дата рождения пользователя.
        sex (CharField): Пол пользователя. Варианты:
            - 'man' (Мужской)
            - 'woman' (Женский)
        height (FloatField): Рост пользователя в сантиметрах.
        weight (FloatField): Вес пользователя в килограммах.
        goal (CharField): Фитнес-цель пользователя. Варианты:
            - 'lose_weight' (Похудение)
            - 'gain_muscle' (Набор массы)
            - 'maintain' (Поддержание формы)
            - 'cutting' (Сушка)
        activity_coef (FloatField): Коэффициент физической активности.
        daily_calories (IntegerField): Дневная норма калорий (ккал).
        daily_water (IntegerField): Дневная норма воды (мл).
        daily_proteins (FloatField): Дневная норма белков (г).
        daily_fats (FloatField): Дневная норма жиров (г).
        daily_carbs (FloatField): Дневная норма углеводов (г).

    Methods:
        save: сохраняет профиль в БД, предварительно расчитав норму калорий, БЖУ и воды.
        __str__: Возвращает строковое представление в формате "Профиль пользователя {username}".

    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateField()
    sex = models.CharField(
        max_length=5, choices=[("man", "Мужской"), ("woman", "Женский")], default="man"
    )
    height = models.FloatField()
    weight = models.FloatField()
    goal = models.CharField(
        max_length=50,
        choices=[
            ("lose_weight", "Похудение"),
            ("gain_muscle", "Набор массы"),
            ("maintain", "Поддержание формы"),
            ("cutting", "Сушка"),
        ],
        default="maintain",
    )
    activity_coef = models.FloatField()
    daily_calories = models.IntegerField(null=True)
    daily_water = models.IntegerField(null=True)
    daily_proteins = models.FloatField(null=True)
    daily_fats = models.FloatField(null=True)
    daily_carbs = models.FloatField(null=True)

    def save(self, *args, **kwargs):
        self.daily_calories = get_user_calories_norm(
            self.sex,
            self.weight,
            self.height,
            self.birth_date,
            self.activity_coef,
            self.goal,
        )

        result = get_user_pfc_norm(self.daily_calories, self.goal)
        print(result)
        print(type(result))

        self.daily_proteins, self.daily_fats, self.daily_carbs = get_user_pfc_norm(
            self.daily_calories, self.goal
        )

        print(self.daily_proteins)

        self.daily_water = get_user_water_norm(
            self.sex,
            self.weight,
            self.height,
            self.activity_coef,
            self.goal,
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Профиль пользователя {self.user.username}"


class UserDailyRecord(models.Model):
    """Модель дневной записи пользователя о питании и весе.

    Содержит данные о ежедневном потреблении калорий, макронутриентов,
    воды и весе пользователя.

    Attributes:
        user (ForeignKey): Связь с моделью User.
        user_date (DateField): Дата записи (берётся день пользователя, с учетом его часового пояса).
        weight (FloatField): Вес пользователя в этот день (необязательное).
        calories (IntegerField): Потребленные калории (ккал).
        proteins (FloatField): Потребленные белки (г).
        fats (FloatField): Потребленные жиры (г).
        carbs (FloatField): Потребленные углеводы (г).
        water (IntegerField): Потребленная вода (мл).

    Meta:
        unique_together: Обеспечивает уникальность комбинации user и date
                         (только одна запись на пользователя в день).
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_date = models.DateField()

    weight = models.FloatField(blank=True, null=True)

    calories = models.IntegerField(default=0)
    proteins = models.FloatField(default=0)
    fats = models.FloatField(default=0)
    carbs = models.FloatField(default=0)
    water = models.IntegerField(default=0)

    class Meta:
        unique_together = [["user", "user_date"]]
