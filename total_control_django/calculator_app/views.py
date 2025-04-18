import json
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from users.models import UserProfile

from .models import FoodEntry, UserCustomFood
from .services import search_fatsecret_food, get_food_details
from .forms import FoodEntryForm, OwnFoodEntryForm


@require_POST
def set_timezone(request):
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        user_timezone = json.loads(request.body).get("timezone")
        if user_timezone:
            request.session["user_timezone"] = user_timezone
            return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)


@login_required
def calculator(request):
    user_timezone = request.session.get("user_timezone", "UTC")

    try:
        tz = ZoneInfo(user_timezone)
        user_now = timezone.now().astimezone(tz)
        today = user_now.date()

        entries = FoodEntry.objects.annotate(
            local_date=TruncDate("date_added", tzinfo=tz)
        ).filter(user=request.user, local_date=today)
    except ZoneInfoNotFoundError:
        entries = FoodEntry.objects.filter(
            user=request.user, date_added__date=timezone.now().date()
        )

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
def own_food_search(request, meal):
    query = request.GET.get("query", "")
    try:
        page = int(request.GET.get("page", 0))
    except ValueError:
        page = 0

    if query:
        context = search_fatsecret_food(query, page=page, translate=False)
        context["meal"] = meal
        return render(request, "calculator_app/own_food_search.html", context)
    return render(request, "calculator_app/own_food_search.html", {"meal": meal})


@login_required
def add_food_entry(request, food_id):
    if food_id.startswith("ucf"):
        try:
            custom_food_id = int(food_id[3:])

            food_details = UserCustomFood.get_food_details(
                user=request.user, food_id=custom_food_id
            )
        except ValueError:
            food_details = None
    else:
        food_details = get_food_details(food_id)

    if not food_details:
        return redirect("calculator")

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
                food_amount = f"{round(amount, 1)} г."
                amount /= 100
                calories = food_details["per_100g"]["calories"]
                proteins = food_details["per_100g"]["proteins"]
                fats = food_details["per_100g"]["fats"]
                carbs = food_details["per_100g"]["carbs"]

            elif unit == "ml":
                food_amount = f"{round(amount, 1)} мл."
                amount /= 100
                calories = food_details["per_100ml"]["calories"]
                proteins = food_details["per_100ml"]["proteins"]
                fats = food_details["per_100ml"]["fats"]
                carbs = food_details["per_100ml"]["carbs"]

            else:
                food_amount = (
                    f"{round(amount, 1)} порций по {food_details["serving_name"]}"
                )
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
                amount=food_amount,
                meal=meal,
            )
            return redirect("calculator")

    form = FoodEntryForm(initial={"amount": 1, "unit": "portion"})
    form.fields["unit"].choices = available_units

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
