import requests
from requests_oauthlib import OAuth1

from django.conf import settings
from googletrans import Translator


def get_fatsecret_client():
    return OAuth1(
        settings.FATSECRET_API_KEY,
        settings.FATSECRET_API_SECRET,
        signature_type="query",
    )


def search_fatsecret_food(query, max_result=10, page=0):

    translator = Translator()

    url = "https://platform.fatsecret.com/rest/server.api"

    try:
        translated_query = translator.translate(query, dest="en").text
    except TypeError:
        translated_query = query

    params = {
        "method": "foods.search",
        "search_expression": translated_query,
        "format": "json",
        "max_results": max_result,
        "page_number": page,
    }

    # Получение блюд по APIшке
    try:
        response = requests.get(
            url, params=params, auth=get_fatsecret_client(), timeout=5
        )
        response.raise_for_status()
        data = response.json()

        if "foods" in data and "food" in data["foods"]:
            # Если будет найден только 1 продукт, то всё равно возвращаем список, а не словарь
            if data["foods"]["total_results"] == '1':
                return [data["foods"]["food"]]
            return data["foods"]["food"]
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
    # Иначе возвращаем пустой список
    return []
