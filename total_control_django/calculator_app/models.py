from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()


class FoodEntry(models.Model):
    """Модель записи о потребленной пище пользователя.

    Содержит информацию о приеме пищи с указанием времени, количества и нутриентов.

    Attributes:
        user (ForeignKey): Связь с пользователем
        food_name (CharField): Название продукта/блюда (макс. 255 символов)
        calories (IntegerField): Калорийность порции (ккал)
        proteins (FloatField): Содержание белков (г)
        fats (FloatField): Содержание жиров (г)
        carbs (FloatField): Содержание углеводов (г)
        amount (CharField): Количество/объем потребления (макс. 255 символов)
        meal (CharField): Прием пищи. Варианты:
            - breakfast (Завтрак)
            - lunch (Обед)
            - dinner (Ужин)
            - snack (Перекус)
        date_added (DateTimeField): Дата и время создания записи (автоматически)

    Methods:
        __str__: Возвращает строку в формате "Название (Количество)"
    """

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
    """Модель пользовательских пищевых продуктов.

    Позволяет пользователям создавать и хранить собственные продукты
    с разными вариантами представления нутриентов.

    Attributes:
        user (ForeignKey): Связь с пользователем
        food_id (AutoField): Уникальный ID продукта (автоинкремент)
        food_name (CharField): Название продукта (макс. 100 символов)
        brand_name (CharField): Бренд/производитель (необязательно)
        serving_name (CharField): Название порции (макс. 100 символов)

        Параметры на порцию (обязательно):
            calories (IntegerField): Калории
            proteins (FloatField): Белки (г)
            fats (FloatField): Жиры (г)
            carbs (FloatField): Углеводы (г)

        Параметры на 100 грамм (необязательно):
            calories_100g (IntegerField)
            proteins_100g (FloatField)
            fats_100g (FloatField)
            carbs_100g (FloatField)

        Параметры на 100 мл (необязательно):
            calories_100ml (IntegerField)
            proteins_100ml (FloatField)
            fats_100ml (FloatField)
            carbs_100ml (FloatField)

        created_at (DateTimeField): Дата создания (автоматически)
        updated_at (DateTimeField): Дата последнего обновления (автоматически)

    Methods:
        to_api_format(): Преобразует объект в словарь для API-ответа
        get_food_details(cls, user, food_id): Получает данные продукта по ID
    """

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
        """Преобразует объект в нужный формат в виде API-ответа.

        Returns:
            dict: Словарь с данными продукта в структурированном виде:
                - food_id: строка с префиксом 'ucf'
                - базовые параметры продукта
                - параметры на порцию
                - параметры на 100г (если есть)
                - параметры на 100мл (если есть)
        """

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
    def get_food_details(cls, user, food_id: int):
        """Получает данные пользовательского продукта.

        Args:
            user (User): Объект пользователя
            food_id (int): ID продукта

        Returns:
            dict/None: Данные продукта в API-формате или None если не найден
        """

        try:
            food = cls.objects.get(user=user, food_id=food_id)
            return food.to_api_format()
        except cls.DoesNotExist:
            return None


class UserFavoriteCustomFood(models.Model):
    """Модель для хранения избранных пользовательских продуктов.

    Attributes:
        user (ForeignKey): Связь с пользователем
        custom_food (ForeignKey): Связь с пользовательским продуктом
        created_at (DateTimeField): Дата добавления в избранное (автоматически)
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    custom_food = models.ForeignKey(UserCustomFood, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class UserFavoriteApiFood(models.Model):
    """Модель для хранения избранных продуктов из внешнего API.

    Attributes:
        user (ForeignKey): Связь с пользователем
        food_id (IntegerField): ID продукта в внешней системе
        food_name (CharField): Название продукта (макс. 100 символов)
        brand_name (CharField): Бренд продукта (необязательно)
        food_description (CharField): Описание продукта (макс. 255 символов)
        created_at (DateTimeField): Дата добавления в избранное (автоматически)
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_id = models.IntegerField()
    food_name = models.CharField(max_length=100)
    brand_name = models.CharField(max_length=100, null=True, blank=True)
    food_description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
