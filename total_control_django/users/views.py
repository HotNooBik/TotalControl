from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages

from .forms import UserRegisterForm, UserLoginForm, UserProfileForm
from .models import UserProfile
from .utils.nutrition import get_users_calorie_norm, get_users_pfc_norm, get_users_water_norm


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Вы успешно зарегистрировались!")
            return redirect("main")
    else:
        form = UserRegisterForm()
    return render(request, "users/register.html", {"form": form})


def user_login(request):
    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Вы вошли в систему!")
            return redirect("main")
    else:
        form = UserLoginForm()
    return render(request, "users/login.html", {"form": form})


def user_logout(request):
    logout(request)
    messages.info(request, "Вы вышли из системы.")
    return redirect("main")


@login_required
def profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    return render(request, "users/profile.html", {"profile": user_profile})


@login_required
def edit_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == "POST":
        if "cancel" in request.POST:
            messages.info(request, "Изменения отменены.")
            return redirect("profile")

        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            updated_profile = form.save(commit=False)

            # Пересчёт дневной нормы калорий и БЖУ
            daily_calories = get_users_calorie_norm(
                updated_profile.sex,
                updated_profile.weight,
                updated_profile.height,
                updated_profile.birth_date,
                updated_profile.activity_coef,
                updated_profile.goal,
            )
            updated_profile.daily_calories = daily_calories
            daily_proteins, daily_fats, daily_carbs = get_users_pfc_norm(
                daily_calories, updated_profile.goal
            )
            updated_profile.daily_proteins = daily_proteins
            updated_profile.daily_fats = daily_fats
            updated_profile.daily_carbs = daily_carbs
            daily_water = get_users_water_norm(
                updated_profile.sex,
                updated_profile.weight,
                updated_profile.height,
                updated_profile.activity_coef,
                updated_profile.goal,
            )
            updated_profile.daily_water = daily_water

            updated_profile.save()
            messages.success(request, "Данные профиля успешно обновлены!")
            return redirect("profile")
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, "users/edit_profile.html", {"form": form})
