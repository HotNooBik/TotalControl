from django.shortcuts import render

from .services import search_fatsecret_food


def search_food(request):
    query = request.GET.get("q")
    page = int (request.GET.get('page', 0))

    results = search_fatsecret_food(query, page=page)

    return render(
        request, "nutrition/search.html", {"results": results, "query": query}
    )
