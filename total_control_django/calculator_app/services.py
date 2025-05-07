from pprint import pprint

import io
import json
import base64
from PIL import Image
import requests

from requests_oauthlib import OAuth1
from googletrans import Translator

from django.conf import settings

from users.models import UserDailyRecord

from .models import UserCustomFood, UserFavoriteApiFood, UserFavoriteCustomFood

from .prompts import FOOD_RECOGNITION_PROMPT, MODEL_VERSION


TRANSLATOR = Translator()  # Модуль для перевода текста


def get_fatsecret_client(query=True):
    """
    Создаёт OAuth1 клиент для аутентификации в API FatSecret.

    Использует ключи из настроек Django (FATSECRET_API_KEY и FATSECRET_API_SECRET).

    Returns:
        OAuth1: Авторизованный OAuth1 клиент для выполнения запросов к FatSecret API.
    """

    return OAuth1(
        settings.FATSECRET_API_KEY,
        settings.FATSECRET_API_SECRET,
        signature_type="query" if query else "auth_header",
    )


def search_fatsecret_food(
    query, max_results: int = 5, page: int = 0, translate: bool = False
) -> dict:
    """
    Выполняет поиск продуктов в базе данных FatSecret по заданному запросу.

    Args:
        query (str): Поисковый запрос для поиска продуктов.
        max_results (int, optional): Максимальное количество результатов на странице. По умолчанию 5.
        page (int, optional): Номер страницы для пагинации (начинается с нуля). По умолчанию 0.
        translate (bool, optional): Флаг необходимости перевода описания и названия на русский язык. По умолчанию False.

    Returns:
        dict: Словарь с результатами поиска, содержащий следующие ключи:
            - 'query' (str): Исходный поисковый запрос.
            - 'results' (list): Список найденных продуктов.
            - 'current_page' (int): Текущая страница.
            - 'total_pages' (int): Общее количество страниц.
    """

    try:
        translated_query = TRANSLATOR.translate(query, dest="en").text
    except TypeError:
        translated_query = query

    url = "https://platform.fatsecret.com/rest/server.api"
    params = {
        "method": "foods.search",
        "search_expression": translated_query,
        "format": "json",
        "max_results": max_results,
        "page_number": page,
    }

    context = {
        "query": query,
        "results": None,
        "current_page": page,
        "total_pages": None,
    }

    try:
        response = requests.get(
            url, params=params, auth=get_fatsecret_client(), timeout=5
        )
        response.raise_for_status()
        data = response.json()

        if "foods" in data and "food" in data["foods"]:
            # Если будет найден только 1 продукт, то всё равно возвращаем список, а не словарь
            if isinstance(data["foods"]["food"], dict):
                result = [data["foods"]["food"]]
            else:
                result = data["foods"]["food"]

            if translate:
                for food in result:
                    food["food_description"] = TRANSLATOR.translate(
                        food["food_description"], dest="ru"
                    ).text
                    food["food_name"] = TRANSLATOR.translate(
                        food["food_name"], dest="ru"
                    ).text
                    food["food_type"] = TRANSLATOR.translate(
                        food["food_type"], dest="ru"
                    ).text

            context["results"] = result
            context["total_pages"] = (
                int(data["foods"]["total_results"]) - 1
            ) // max_results

            # pprint(context)
            return context

    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")

    # Иначе возвращаем пустой список
    return context


def get_food_details(food_id: str | int) -> dict | None:
    """
    Получает детальную информацию о продукте по его ID из API FatSecret.

    Args:
        food_id (str | int): Уникальный идентификатор продукта.

    Returns:
        dict | None: Словарь с информацией о продукте или None, если произошла ошибка. Ключи:
            - 'food_id' (str): ID продукта.
            - 'food_name' (str): Название продукта.
            - 'serving_name' (str): Стандартная порция.
            - 'brand_name' (str | None): Бренд (если есть).
            - 'image' (str | None): URL изображения продукта (если есть).
            - 'food_description' (str): Описание с КБЖУ продукта.
            - 'per_portion' (dict): Питательные вещества на одну порцию.
            - 'per_100g' (dict): Питательные вещества на 100 грамм.
            - 'per_100ml' (dict): Питательные вещества на 100 мл (для жидких продуктов).
    """

    url = "https://platform.fatsecret.com/rest/server.api"
    params = {
        "method": "food.get.v4",
        "food_id": food_id,
        "format": "json",
        "include_food_images": True,
        "flag_default_serving": True,
    }

    try:
        response = requests.get(
            url, params=params, auth=get_fatsecret_client(), timeout=5
        )
        response.raise_for_status()
        data = response.json()

        if "food" in data:
            food = data["food"]

            image = None
            brand_name = None

            if food["food_type"] == "Brand":
                brand_name = food["brand_name"]
            elif "food_images" in food:
                image = food["food_images"]["food_image"][0][
                    "image_url"
                ]  # Картинки есть только у небрэндовой еды

            # Получаем название одной порции
            serving_description = get_default_serving_description(
                food["servings"]["serving"]
            )

            result = extract_nutrition_data(food["servings"]["serving"])

            context = {
                "food_id": food["food_id"],
                "food_name": food["food_name"],
                "serving_name": serving_description,
                "brand_name": brand_name,
                "image": image,
                "food_description": f'На "{serving_description}" - '
                f'Калорий: {result.get("per_portion", {}).get("calories", 0)} ккал. | '
                f'Жиров: {result.get("per_portion", {}).get("fats", 0)} г. | '
                f'Углеводов: {result.get("per_portion", {}).get("carbs", 0)} г. | '
                f'Белков: {result.get("per_portion", {}).get("proteins", 0)} г.',
            }

            context = context | result

            return context

    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса еды по айди: {e}")
    return None


def get_default_serving_description(servings: list) -> str:
    """
    Находит название стандартной порции среди списка порций.

    Args:
        servings (list): Список порций, полученный из данных продукта.

    Returns:
        str: Описание стандартной порции. Если такая не найдена — возвращает '100 g'.
    """
    serving_description = None
    for serving in servings:
        if serving.get("is_default") == "1":
            serving_description = serving.get("serving_description")
    return serving_description if serving_description else "100 g"


def extract_nutrition_data(servings: list) -> dict:
    """
    Обрабатывает данные о порциях и извлекает информацию о питательной ценности.

    Args:
        servings (list): Список порций из данных продукта.

    Returns:
        dict: Содержит три ключа:
            - 'per_portion' (dict): Данные на стандартную порцию.
            - 'per_100g' (dict): Данные на 100 грамм.
            - 'per_100ml' (dict): Данные на 100 мл.

            Каждое значение — это словарь с ключами:
                - 'calories' (int): калории (ккал),
                - 'proteins' (float): белки (г),
                - 'fats' (float): жиры (г),
                - 'carbs' (float): углеводы (г).
    """
    result = {"per_portion": None, "per_100g": None, "per_100ml": None}

    def create_nutrition_dict(serving, multiplier=1.0):
        return {
            "calories": round(float(serving["calories"]) * multiplier),
            "proteins": round(float(serving["protein"]) * multiplier, 1),
            "fats": round(float(serving["fat"]) * multiplier, 1),
            "carbs": round(float(serving["carbohydrate"]) * multiplier, 1),
        }

    # Обработка per_portion (если не будет is_default)
    if servings:
        result["per_portion"] = create_nutrition_dict(servings[0])

    for serving in servings:
        unit = serving.get("metric_serving_unit", "")
        amount = float(serving.get("metric_serving_amount", 1))
        serving_description = serving.get("serving_description")
        serving_description = serving_description if serving_description else ""

        # Получаем КБЖУ на одну стандартную порцию (по умолчанию)
        if not result["per_portion"] and serving.get("is_default") == "1":
            result["per_portion"] = create_nutrition_dict(serving)

        # Получаем КБЖУ на 100 грамм продукта
        if not result["per_100g"]:
            if serving_description.startswith("100 g"):
                result["per_100g"] = create_nutrition_dict(serving)
            elif unit == "g":
                result["per_100g"] = create_nutrition_dict(serving, 100 / amount)
            elif serving_description.startswith("1 oz") or unit == "oz":
                multiplier = (
                    100 / 29.57353
                    if serving_description.startswith("1 oz")
                    else 100 / (amount * 29.57353)
                )
                result["per_100g"] = create_nutrition_dict(serving, multiplier)

        # Получаем КБЖУ на 100 миллилитров продукта
        if not result["per_100ml"]:
            if serving_description.startswith("100 ml"):
                result["per_100ml"] = create_nutrition_dict(serving)
            elif serving_description.startswith("1 fl oz") or unit == "fl oz":
                multiplier = (
                    100 / 29.57353
                    if serving_description.startswith("1 fl oz")
                    else 100 / (amount * 29.57353)
                )
                result["per_100ml"] = create_nutrition_dict(serving, multiplier)
            elif unit == "ml":
                result["per_100ml"] = create_nutrition_dict(serving, 100 / amount)
            elif serving_description == "1 cup":
                result["per_100ml"] = create_nutrition_dict(serving, 100 / 236.58824)
            elif serving_description == "1 tbsp":
                result["per_100ml"] = create_nutrition_dict(serving, 100 / 14.78676)
            elif serving_description == "1 tsp":
                result["per_100ml"] = create_nutrition_dict(serving, 100 / 4.92892)

    return result


def get_products_from_image(image_path):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    base64_image = prepare_image(image_path)
    data_url = f"data:image/jpeg;base64,{base64_image}"

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": FOOD_RECOGNITION_PROMPT},
                {"type": "image_url", "image_url": {"url": data_url}},
            ],
        }
    ]

    payload = {"model": MODEL_VERSION, "messages": messages}

    response = requests.post(url, headers=headers, json=payload, timeout=60)

    answer = (
        response.json().get("choices", [{}])[0].get("message", {}).get("content", None)
    )

    if not answer:
        return None

    try:
        result = json.loads(answer)
    except json.JSONDecodeError as e:
        print(f"Ошибка парсинга JSON: {e}")
        result = None

    return result


def prepare_image(image_path, max_size=1280, quality=85):
    """
    Подготавливает изображение для передачи: сжимает до заданного размера с сохранением пропорций, 
    конвертирует в формат JPEG вместе с RGB и кодирует в base64. При увеличении разрешения
    повышает качество с помощью ресемплинга LANCZOS.

    Args:
        image_path (str): Путь к исходному изображению.
        max_size (int, необязательный): Максимальный размер большей стороны изображения. 
                                        По умолчанию 1280 пикселей.
        quality (int, необязательный): Качество сохраняемого JPEG-файла (от 1 до 95).
                                       По умолчанию 85.

    Returns:
        str: Строка с изображением, закодированным в формате base64.
    """
    with Image.open(image_path) as img:
        if img.mode != "RGB":
            img = img.convert("RGB")

        width, height = img.size

        if width > height:
            target_width = max_size
            target_height = int((max_size / width) * height)
        else:
            target_height = max_size
            target_width = int((max_size / height) * width)

        resized_img = img.resize(
            (target_width, target_height), resample=Image.Resampling.LANCZOS
        )

        buffer = io.BytesIO()
        resized_img.save(buffer, format="JPEG", quality=quality)
        buffer.seek(0)

        return base64.b64encode(buffer.read()).decode("utf-8")


def search_user_custom_food(
    user, query: str, max_results: int = 5, page: int = 0
) -> dict:
    """
    Выполняет поиск пользовательских продуктов (добавленных вручную) по имени.

    Args:
        user (User): Объект пользователя.
        query (str): Поисковый запрос.
        max_results (int, optional): Максимальное количество результатов на странице. По умолчанию 5.
        page (int, optional): Номер страницы. По умолчанию 0.

    Returns:
        dict: Словарь с результатами поиска, содержащий следующие ключи:
            - 'query' (str): Исходный поисковый запрос.
            - 'results' (list): Список найденных продуктов.
            - 'current_page' (int): Текущая страница.
            - 'total_pages' (int): Общее количество страниц.
    """

    filtered_user_foods = UserCustomFood.objects.filter(
        user=user, food_name__icontains=query  # нечувствительный к регистру поиск
    )

    total_items = filtered_user_foods.count()
    total_pages = (total_items - 1) // max_results if total_items > 0 else 0

    foods_on_page = filtered_user_foods.order_by("-created_at")[
        max_results * page : max_results * page + max_results
    ]

    result = list(
        foods_on_page.values(
            "brand_name",
            "food_name",
            "food_id",
            "serving_name",
            "calories",
            "proteins",
            "carbs",
            "fats",
            "calories_100g",
            "calories_100ml",
        )
    )

    processed_result = [
        {
            "food_id": "ucf" + str(food["food_id"]),
            "brand_name": food["brand_name"],
            "food_name": food["food_name"],
            "food_description": (
                f'На "{food["serving_name"]}" - '
                f'Калорий: {food["calories"]} ккал. | '
                f'Жиров: {food["fats"]} г. | '
                f'Углеводов: {food["carbs"]} г. | '
                f'Белков: {food["proteins"]} г.'
            ),
            "has_g": bool(food["calories_100g"]),
            "has_ml": bool(food["calories_100ml"]),
        }
        for food in result
    ]

    context = {
        "current_page": page,
        "query": query,
        "results": processed_result,
        "total_pages": total_pages,
    }

    return context


def search_user_favorite_food(
    user, query: str, max_results: int = 5, page: int = 0
) -> dict:
    """
    Выполняет поиск избранных продуктов пользователя (включая API и пользовательские) по имени.

    Args:
        user (User): Объект пользователя.
        query (str): Поисковый запрос.
        max_results (int, optional): Максимальное количество результатов на странице. По умолчанию 5.
        page (int, optional): Номер страницы. По умолчанию 0.

    Returns:
        dict: Словарь с результатами поиска, содержащий следующие ключи:
            - 'query' (str): Исходный поисковый запрос.
            - 'results' (list): Список найденных продуктов.
            - 'current_page' (int): Текущая страница.
            - 'total_pages' (int): Общее количество страниц.
    """

    custom_favorites = UserFavoriteCustomFood.objects.filter(
        user=user, food_name__icontains=query
    )

    api_favorites = UserFavoriteApiFood.objects.filter(
        user=user, food_name__icontains=query
    )

    # Сортируем по дате создания
    all_favorites = list(custom_favorites) + list(api_favorites)
    all_favorites.sort(key=lambda item: item.created_at, reverse=True)

    total_items = len(all_favorites)
    total_pages = (total_items - 1) // max_results if total_items > 0 else 0

    favorites_on_page = all_favorites[
        max_results * page : max_results * page + max_results
    ]

    processed_result = []
    for food in favorites_on_page:
        base_data = {
            "brand_name": food.brand_name,
            "food_name": food.food_name,
            "food_description": food.food_description,
        }
        if isinstance(food, UserFavoriteCustomFood):
            base_data["food_id"] = f"ucf{food.custom_food_id}"
        elif isinstance(food, UserFavoriteApiFood):
            base_data["food_id"] = food.food_id
        processed_result.append(base_data)

    context = {
        "current_page": page,
        "query": query,
        "results": processed_result,
        "total_pages": total_pages,
    }

    return context


def get_weight_history_for_chart(user, limit=0, period="all", get_info=False):
    """
    Получает данные о весе пользователя за указанный период (историю) для построения графика.

    Группирует записи по дате и возвращает списки меток (дат) и значений веса,
    которые можно использовать для отображения в графическом интерфейсе.

    Args:
        user (User): Объект пользователя, чьи записи о весе необходимо получить.
        limit (int, optional): Ограничение количества возвращаемых записей.
                               Если > 0 — возвращает последние N записей.
                               Если 0 — без ограничения. По умолчанию 0.
        period (str, optional): Период группировки данных. Допустимые значения:
                                 - 'all' — по каждой отдельной дате (по умолчанию),
                                 - 'week' — по неделям,
                                 - 'month' — по месяцам,
                                 - 'year' — по годам. По умолчанию 'all'.
        get_info (bool): Если true, то выводит дополнительную информацию о весе (средний, максимальный и минимальный).

    Returns:
        tuple: Кортеж из двух списков:
            - labels (List[str]): Список строковых представлений дат согласно указанному периоду.
            - data (List[float]): Список значений веса.
            - info(Dict): дополнительная информация о data:
                - mean (float): среднее значение,
                - max (float): максимальное значение,
                - min (float): минимальное значение.
    """

    records = UserDailyRecord.objects.filter(
        user=user,
    ).order_by("user_date")

    grouped_records = []
    if period == "all":
        grouped_records = list(records)
    else:
        period_data = {}
        for record in records:
            if period == "week":
                key = record.user_date.strftime("%Y-%W")
            elif period == "month":
                key = record.user_date.strftime("%Y-%m")
            elif period == "year":
                key = record.user_date.strftime("%Y")
            else:
                raise ValueError(
                    "No such period type. Use 'all', 'week', 'month' or 'year'."
                )
            period_data[key] = record
        grouped_records = sorted(period_data.values(), key=lambda x: x.user_date)

    if limit < 0:
        raise ValueError("Invalid limit value, it must be greater than or equal to 0.")
    elif limit > 0:
        grouped_records = grouped_records[-limit:]

    # Формируем данные для графика
    labels = []
    data = []

    for record in grouped_records:
        if period == "all":
            labels.append(record.user_date.strftime("%d/%m/%Y"))
        elif period == "week":
            labels.append(record.user_date.strftime("№%W - %d/%m/%Y"))
        elif period == "month":
            labels.append(record.user_date.strftime("%m/%Y"))
        else:
            labels.append(record.user_date.strftime("%Y"))
        data.append(round(record.weight, 1))

    if get_info:
        info = {
            "mean": round(sum(data) / len(data), 1),
            "max": max(data),
            "min": min(data),
        }
        return labels, data, info

    else:
        return labels, data, None
