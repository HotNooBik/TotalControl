import requests


def get_product_by_barcode(barcode: str):
    barcode = "".join(filter(str.isdigit, barcode))

    url = f"https://world.openfoodfacts.net/api/v2/product/{barcode}?product_type=all&fields=product_name%2Cnutriments%2Cbrands"

    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()

    if data.get("status") != 1:
        return None

    product = data.get("product", {})
    nutriments = product.get("nutriments", {})

    return {
        "food_name": product.get("product_name", "Без названия"),
        "brand_name": product.get("brands", ""),
        "calories": nutriments.get("energy-kcal_100g", 0),
        "proteins": round(nutriments.get("proteins_100g", 0), 1),
        "fats": round(nutriments.get("fat_100g", 0), 1),
        "carbs": round(nutriments.get("carbohydrates_100g", 0), 1),
    }
