from functools import wraps
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect
from django.utils import timezone

from .forms import UserRegisterForm, UserLoginForm, UserProfileForm
from .models import UserProfile, UserDailyRecord


def anonymous_required(view_func):
    """Декоратор, который проверяет, чтобы пользователь не был авторизованным (иначе отправляет на главную страницу)."""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("main"))
        return view_func(request, *args, **kwargs)

    return wrapper


@anonymous_required
def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("main")
    else:
        form = UserRegisterForm()
    return render(request, "users/register.html", {"form": form})


@anonymous_required
def user_login(request):
    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("main")
    else:
        form = UserLoginForm()
    return render(request, "users/login.html", {"form": form})


def user_logout(request):
    logout(request)
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
            return redirect("profile")

        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            updated_profile = form.save(commit=False)
            updated_profile.save()

            user_profile = get_object_or_404(UserProfile, user=request.user)
            try:
                tz = ZoneInfo(user_profile.timezone)
                today = timezone.now().astimezone(tz).date()
            except ZoneInfoNotFoundError:
                today = timezone.now().date()
            
            UserDailyRecord.objects.update_or_create(
                user=request.user,
                user_date=today,
                defaults={
                    "weight": user_profile.weight,
                    "calories_goal": user_profile.daily_calories,
                    "proteins_goal": user_profile.daily_proteins,
                    "fats_goal": user_profile.daily_fats,
                    "carbs_goal": user_profile.daily_carbs,
                    "water_goal": user_profile.daily_water,
                }
            )
            return redirect("profile")
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, "users/edit_profile.html", {"form": form})
