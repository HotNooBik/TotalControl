from pprint import pprint
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from urllib.parse import urlencode
from pyzbar.pyzbar import decode
from PIL import Image

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone

from users.models import UserProfile, UserDailyRecord

from calculator_app.models import FoodEntry
from calculator_app.forms import FoodEntryForm

from .services import get_product_by_barcode
from .forms import BarcodeUploadForm


@login_required
def barcode_image_scanning(request):

    prev_url = request.GET.get("prev", reverse("calculator"))

    meal = request.GET.get("meal", "snack")
    if meal not in ["breakfast", "lunch", "dinner", "snack"]:
        meal = "snack"

    error = request.GET.get("error", "")

    context = {
        "prev_url": prev_url,
        "meal": meal,
    }

    if request.method == "POST":
        form = BarcodeUploadForm(request.POST, request.FILES)

        if form.is_valid():
            manual_code = form.cleaned_data.get("manual_code")
            image_file = form.cleaned_data.get("image")
            decoded_text = None

            if image_file:
                image = Image.open(image_file)
                decoded_objects = decode(image)
                if decoded_objects:
                    decoded_text = decoded_objects[0].data.decode("utf-8").strip()

            final_code = decoded_text or manual_code
            if final_code:
                params = urlencode({"meal": meal, "prev": prev_url})
                return redirect(
                    f"{reverse('add_barcode_food', kwargs={'barcode': final_code})}?{params}"
                )
            else:
                context["error"] = "Не удалось распознать код."
        else:
            context["error"] = (
                "Добавьте изображение со штрих-кодом или введите его вручную!"
            )
    else:
        form = BarcodeUploadForm()
        if error == "not found":
            context["error"] = "Не удалось найти продукт по данному коду."
        else:
            context["show_hello"] = True

    context["form"] = form

    return render(
        request,
        "scanner/barcode_scanning.html",
        context,
    )


@login_required
def add_barcode_food(request, barcode: str):

    prev_url = request.GET.get("prev", reverse("calculator"))

    meal = request.GET.get("meal", "snack")
    if meal not in ["breakfast", "lunch", "dinner", "snack"]:
        meal = "snack"

    context = {
        "prev_url": prev_url,
        "meal": meal,
    }

    product_data = get_product_by_barcode(barcode)

    if not product_data:
        params = urlencode({"meal": meal, "prev": prev_url, "error": "not found"})
        return redirect(f"{reverse('barcode_scanning')}?{params}")

    if request.method == "POST":
        post_data = request.POST.copy()
        post_data["unit"] = "g"
        form = FoodEntryForm(post_data)
        form.fields["unit"].choices = [("g", "Граммы")]

        if form.is_valid():
            amount = form.cleaned_data.get("amount")

            user_profile = get_object_or_404(UserProfile, user=request.user)
            try:
                tz = ZoneInfo(user_profile.timezone)
                today = timezone.now().astimezone(tz).date()
            except ZoneInfoNotFoundError:
                today = timezone.now().date()

            daily_record, _ = UserDailyRecord.objects.get_or_create(
                user=request.user,
                user_date=today,
            )

            FoodEntry.objects.create(
                food_name=product_data["food_name"],
                calories=round(product_data["calories"] * (amount / 100), 1),
                proteins=round(product_data["proteins"] * (amount / 100), 1),
                fats=round(product_data["fats"] * (amount / 100), 1),
                carbs=round(product_data["carbs"] * (amount / 100), 1),
                amount=f"{round(amount, 1)} г.",
                meal=meal,
                daily_record=daily_record,
            )
            return redirect("calculator")

    context["form"] = FoodEntryForm(initial={"amount": 100})
    context["code"] = barcode
    context["food"] = product_data

    micronutrients_mass = (
        product_data["proteins"] + product_data["fats"] + product_data["carbs"]
    )
    context["proteins_percent"] = (product_data["proteins"] / micronutrients_mass) * 100
    context["fats_percent"] = (product_data["fats"] / micronutrients_mass) * 100
    context["carbs_percent"] = (product_data["carbs"] / micronutrients_mass) * 100

    return render(
        request,
        "scanner/add_barcode_food.html",
        context,
    )
