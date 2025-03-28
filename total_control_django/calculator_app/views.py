from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.decorators import login_required

from users.models import UserProfile

from .models import FoodEntry
from .services import search_fatsecret_food, get_food_details
from .forms import FoodEntryForm


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
        "entries": entries.order_by("date_added"),
        "calories_percent":  calories_percent if calories_percent < 100 else 100,
        "proteins_percent":  proteins_percent if proteins_percent < 100 else 100,
        "fats_percent":  fats_percent if fats_percent < 100 else 100,
        "carbs_percent":  carbs_percent if carbs_percent < 100 else 100,
    }
    return render(request, "calculator_app/calculator.html", context)


@login_required
def delete_entry(request, entry_id):
    entry = get_object_or_404(FoodEntry, id=entry_id, user=request.user)
    entry.delete()
    return redirect("calculator")


@login_required
def food_search(request):
    query = request.GET.get('query', '')
    try:
        page = int(request.GET.get('page', 0))
    except ValueError:
        page = 0
    
    if query:
        context = search_fatsecret_food(query, page=page, translate=False)
        return render(request, 'calculator_app/food_search.html', context)
    return render(request, 'calculator_app/food_search.html')


@login_required
def add_food_entry(request, food_id):
    # Получаем детали продукта из API
    food_details = get_food_details(food_id)

    if not food_details:
        return redirect('food_search')
    
    if request.method == 'POST':
        form = FoodEntryForm(request.POST)
        if form.is_valid():
            # Создаем запись
            FoodEntry.objects.create(
                user=request.user,
                food_name=food_details['name'],
                calories=round(food_details['calories'] * form.cleaned_data['grams'] / 100),
                proteins=round(food_details['proteins'] * form.cleaned_data['grams'] / 100, 1),
                fats=round(food_details['fats'] * form.cleaned_data['grams'] / 100, 1),
                carbs=round(food_details['carbs'] * form.cleaned_data['grams'] / 100, 1),
                grams=round(form.cleaned_data['grams'], 1)
            )
            return redirect('calculator')
    else:
        form = FoodEntryForm(initial={'grams': 100})
    
    context = {
        'food': food_details,
        'form': form,
    }
    return render(request, 'calculator_app/add_food_entry.html', context)