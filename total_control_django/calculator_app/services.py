from pprint import pprint
import requests

from requests_oauthlib import OAuth1
from googletrans import Translator

from django.conf import settings

from .models import UserCustomFood, UserFavoriteApiFood, UserFavoriteCustomFood


TRANSLATOR = Translator()


def get_fatsecret_client():
    return OAuth1(
        settings.FATSECRET_API_KEY,
        settings.FATSECRET_API_SECRET,
        signature_type="query",
    )


def search_fatsecret_food(
    query, max_results: int = 5, page: int = 0, translate: bool = False
) -> dict:

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

            pprint(context)
            return context

    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")

    # Иначе возвращаем пустой список
    return context


def get_food_details(food_id: str | int) -> dict | None:

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
    serving_description = None
    for serving in servings:
        if serving.get("is_default") == "1":
            serving_description = serving.get("serving_description")
    return serving_description if serving_description else "100 g"


def extract_nutrition_data(servings: list) -> dict:
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


def search_user_custom_food(
    user, query: str, max_results: int = 5, page: int = 0
) -> dict:

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
