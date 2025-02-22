from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm
from .models import UserProfile


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Вы успешно зарегистрировались!')
            return redirect('main')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


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
    return render(request, 'users/profile.html', {'profile': user_profile})
