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

            pprint(result)

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
                image = food["food_images"]["food_image"][0]["image_url"]   # Картинки есть только у не брэндовой еды

            if isinstance(food["servings"]["serving"], list):
                return {
                    "id": food["food_id"],
                    "name": food["food_name"],
                    "calories": float(food["servings"]["serving"][0]["calories"]),
                    "proteins": float(food["servings"]["serving"][0]["protein"]),
                    "fats": float(food["servings"]["serving"][0]["fat"]),
                    "carbs": float(food["servings"]["serving"][0]["carbohydrate"]),
                    "brand_name": brand_name,
                    "image": image,
                }
            return {
                "id": food["food_id"],
                "name": food["food_name"],
                "calories": float(food["servings"]["serving"]["calories"]),
                "proteins": float(food["servings"]["serving"]["protein"]),
                "fats": float(food["servings"]["serving"]["fat"]),
                "carbs": float(food["servings"]["serving"]["carbohydrate"]),
                "brand_name": brand_name,
            }

    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса еды по айди: {e}")
    return None
