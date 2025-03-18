import requests
from requests_oauthlib import OAuth1

from django.shortcuts import render
from django.conf import settings
from googletrans import Translator


def search_food(request):
    translator = Translator()
    results = []
    query = request.GET.get("q", "")

    if query:
        # Параметры запроса к FatSecret API
        url = "https://platform.fatsecret.com/rest/server.api"
        params = {
            "method": "foods.search",
            "search_expression": translator.translate(query, dest="en").text,
            "format": "json",
            "max_results": 10,
        }

        # Аутентификация OAuth1
        auth = OAuth1(
            settings.FATSECRET_API_KEY,
            settings.FATSECRET_API_SECRET,
            signature_type="query",
        )

        # Получение блюд по APIшке
        try:
            response = requests.get(url, params=params, auth=auth, timeout=5)
            response.raise_for_status()
            data = response.json()

            # Обработка ответа
            if "foods" in data and "food" in data["foods"]:

                # ДАННУЮ ЧАСТЬ НАДО ПЕРЕПИСАТЬ, СЛИШКОМ МНОГО КУШАЕТ РЕСУРСОВ
                for i in range(len(data["foods"]["food"])):
                    data["foods"]["food"][i]["food_name"] = translator.translate(
                        data["foods"]["food"][i]["food_name"], dest="ru"
                    ).text

                results = data["foods"]["food"]

        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}")

    return render(
        request, "nutrition/search.html", {"results": results, "query": query}
    )
