from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.decorators import login_required

from users.models import UserProfile

from .models import FoodEntry
from .services import search_fatsecret_food, get_food_details
from .forms import FoodEntryForm, OwnFoodEntryForm


@login_required
def calculator(request):
    today = timezone.now().date()

    entries = FoodEntry.objects.filter(user=request.user, date_added__date=today)
    totals = entries.aggregate(
        calories=Sum("calories"),
        proteins=Sum("proteins"),
        fats=Sum("fats"),
        carbs=Sum("carbs"),
    )

    breakfast_entries = entries.filter(meal="breakfast")
    lunch_entries = entries.filter(meal="lunch")
    dinner_entries = entries.filter(meal="dinner")
    snack_entries = entries.filter(meal="snack")

    user_profile = get_object_or_404(UserProfile, user=request.user)
    calories_percent = (totals["calories"] or 0) / user_profile.daily_calories * 100
    proteins_percent = (totals["proteins"] or 0) / user_profile.daily_proteins * 100
    fats_percent = (totals["fats"] or 0) / user_profile.daily_fats * 100
    carbs_percent = (totals["carbs"] or 0) / user_profile.daily_carbs * 100

    context = {
        "current_calories": totals["calories"] or 0,
        "current_proteins": totals["proteins"] or 0,
        "current_fats": totals["fats"] or 0,
        "current_carbs": totals["carbs"] or 0,
        "daily_calories": user_profile.daily_calories,
        "daily_proteins": user_profile.daily_proteins,
        "daily_fats": user_profile.daily_fats,
        "daily_carbs": user_profile.daily_carbs,
        "breakfast_entries": breakfast_entries.order_by("date_added"),
        "lunch_entries": lunch_entries.order_by("date_added"),
        "dinner_entries": dinner_entries.order_by("date_added"),
        "snack_entries": snack_entries.order_by("date_added"),
        "calories_percent": calories_percent if calories_percent < 100 else 100,
        "proteins_percent": proteins_percent if proteins_percent < 100 else 100,
        "fats_percent": fats_percent if fats_percent < 100 else 100,
        "carbs_percent": carbs_percent if carbs_percent < 100 else 100,
    }
    return render(request, "calculator_app/calculator.html", context)


@login_required
def delete_entry(request, entry_id):
    entry = get_object_or_404(FoodEntry, id=entry_id, user=request.user)
    entry.delete()
    return redirect("calculator")


@login_required
def food_search(request, meal):
    query = request.GET.get("query", "")
    try:
        page = int(request.GET.get("page", 0))
    except ValueError:
        page = 0

    if query:
        context = search_fatsecret_food(query, page=page, translate=False)
        context["meal"] = meal
        return render(request, "calculator_app/food_search.html", context)
    return render(request, "calculator_app/food_search.html", {"meal": meal})


@login_required
def add_food_entry(request, food_id):

    # Получаем детали продукта из API
    food_details = get_food_details(food_id)
    if not food_details:
        return redirect("food_search")

    meal = request.GET.get("meal", "snack")
    if meal not in ["breakfast", "lunch", "dinner", "snack"]:
        meal = "snack"

    available_units = [("portion", "Порции")]
    if food_details.get("per_100g"):
        available_units.append(("g", "Граммы"))
    if food_details.get("per_100ml"):
        available_units.append(("ml", "Милилитры"))

    if request.method == "POST":
        form = FoodEntryForm(request.POST)
        form.fields["unit"].choices = available_units
        if form.is_valid():
            unit = form.cleaned_data["unit"]
            amount = form.cleaned_data["amount"]

            if unit == "g":
                amount /= 100
                calories = food_details["per_100g"]["calories"]
                proteins = food_details["per_100g"]["proteins"]
                fats = food_details["per_100g"]["fats"]
                carbs = food_details["per_100g"]["carbs"]
            elif unit == "ml":
                amount /= 100
                calories = food_details["per_100ml"]["calories"]
                proteins = food_details["per_100ml"]["proteins"]
                fats = food_details["per_100ml"]["fats"]
                carbs = food_details["per_100ml"]["carbs"]
            else:
                calories = food_details["per_portion"]["calories"]
                proteins = food_details["per_portion"]["proteins"]
                fats = food_details["per_portion"]["fats"]
                carbs = food_details["per_portion"]["carbs"]

            # Создаем запись
            FoodEntry.objects.create(
                user=request.user,
                food_name=food_details["name"],
                calories=round(calories * amount, 1),
                proteins=round(proteins * amount, 1),
                fats=round(fats * amount, 1),
                carbs=round(carbs * amount, 1),
                grams=round(amount if unit == "portion" else amount * 100, 1),
                meal=meal,
            )
            return redirect("calculator")

    form = FoodEntryForm(initial={"amount": 1, "unit": "portion"})
    form.fields["unit"].choices = available_units

    print(food_details)

    micronutrients_mass = sum(
        [
            food_details["per_portion"]["proteins"],
            food_details["per_portion"]["fats"],
            food_details["per_portion"]["carbs"],
        ]
    )
    proteins_percent = 0
    fats_percent = 0
    carbs_percent = 0
    if micronutrients_mass > 0:
        proteins_percent = food_details["per_portion"]["proteins"] / micronutrients_mass
        fats_percent = food_details["per_portion"]["fats"] / micronutrients_mass
        carbs_percent = food_details["per_portion"]["carbs"] / micronutrients_mass

    context = {
        "meal": meal,
        "food": food_details,
        "form": form,
        "available_units": available_units,
        "proteins_percent": proteins_percent * 100,
        "fats_percent": fats_percent * 100,
        "carbs_percent": carbs_percent * 100,
    }
    return render(request, "calculator_app/add_food_entry.html", context)


@login_required
def add_own_food_entry(request):

    meal = request.GET.get("meal", "snack")
    if meal not in ["breakfast", "lunch", "dinner", "snack"]:
        meal = "snack"

    if request.method == "POST":
        form = OwnFoodEntryForm(request.POST)
        if form.is_valid():
            # Создаем запись
            FoodEntry.objects.create(
                user=request.user,
                food_name=form.cleaned_data["food_name"],
                calories=round(form.cleaned_data["calories"]),
                proteins=round(form.cleaned_data["proteins"], 1),
                fats=round(form.cleaned_data["fats"], 1),
                carbs=round(form.cleaned_data["carbs"], 1),
                meal=meal,
            )
            return redirect("calculator")
    else:
        form = OwnFoodEntryForm()

    context = {
        "form": form,
        "meal": meal,
    }

    return render(request, "calculator_app/add_own_food_entry.html", context)
