from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from users.models import UserProfile
from .models import FoodEntry


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

    context = {
        "current_calories": totals["calories"] or 0,
        "current_proteins": totals["proteins"] or 0,
        "current_fats": totals["fats"] or 0,
        "current_carbs": totals["carbs"] or 0,
        "daily_calories": user_profile.daily_calories,
        "daily_proteins": user_profile.daily_proteins,
        "daily_fats": user_profile.daily_fats,
        "daily_carbs": user_profile.daily_carbs,
        "entries": entries.order_by("-date_added"),
    }
    return render(request, "calculator_app/calculator.html", context)


@login_required
def delete_entry(request, entry_id):
    entry = get_object_or_404(FoodEntry, id=entry_id, user=request.user)
    entry.delete()
    return redirect("calculator")
