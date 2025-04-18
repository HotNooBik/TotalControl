from pprint import pprint
import requests
from requests_oauthlib import OAuth1

from django.conf import settings
from googletrans import Translator


TRANSLATOR = Translator()


def get_fatsecret_client():
    return OAuth1(
        settings.FATSECRET_API_KEY,
        settings.FATSECRET_API_SECRET,
        signature_type="query",
    )


def search_fatsecret_food(query, max_results=5, page=0, translate=False):

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

            # pprint(result)

            context["results"] = result
            context["total_pages"] = (
                int(data["foods"]["total_results"]) - 1
            ) // max_results

            return context

    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")

    # Иначе возвращаем пустой список
    return context


def get_food_details(food_id):

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

        pprint(data)

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
