from pprint import pprint
import json
from datetime import datetime
from urllib.parse import urlencode
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.forms import formset_factory

from users.models import UserProfile, UserDailyRecord

from .models import (
    FoodEntry,
    UserCustomFood,
    UserFavoriteCustomFood,
    UserFavoriteApiFood,
)
from .services import (
    search_fatsecret_food,
    get_food_details,
    search_user_custom_food,
    search_user_favorite_food,
    get_weight_history_for_chart,
    get_products_from_image,
    get_product_by_barcode,
)
from .forms import (
    FoodEntryForm,
    OwnFoodEntryForm,
    UserCustomFoodForm,
    ImageUploadForm,
    ImageFoodEntryForm,
    BarcodeUploadForm,
)
from pyzbar.pyzbar import decode
from PIL import Image


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

    # result = get_products_from_image(r"E:\work_space\TotalControl\total_control_django\static\img\dinner.jpg")
    # pprint(result)

    user_timezone = request.session.get("user_timezone", "UTC")

    try:
        tz = ZoneInfo(user_timezone)
        today = timezone.now().astimezone(tz).date()

        start_of_day = timezone.make_aware(
            datetime.combine(today, datetime.min.time()), tz
        )
        end_of_day = timezone.make_aware(
            datetime.combine(today, datetime.max.time()), tz
        )

        start_of_day_utc = start_of_day.astimezone(timezone.utc)
        end_of_day_utc = end_of_day.astimezone(timezone.utc)

        entries = FoodEntry.objects.filter(
            user=request.user, date_added__range=(start_of_day_utc, end_of_day_utc)
        )

    except ZoneInfoNotFoundError:
        today = timezone.now().date()

        entries = FoodEntry.objects.filter(user=request.user, date_added__date=today)

    totals = entries.aggregate(
        calories=Sum("calories"),
        proteins=Sum("proteins"),
        fats=Sum("fats"),
        carbs=Sum("carbs"),
    )

    record, _ = UserDailyRecord.objects.get_or_create(
        user=request.user,
        user_date=today,
    )
    record.calories = totals["calories"] or 0
    record.proteins = totals["proteins"] or 0
    record.fats = totals["fats"] or 0
    record.carbs = totals["carbs"] or 0
    record.save()

    breakfast_entries = entries.filter(meal="breakfast")
    lunch_entries = entries.filter(meal="lunch")
    dinner_entries = entries.filter(meal="dinner")
    snack_entries = entries.filter(meal="snack")

    user_profile = get_object_or_404(UserProfile, user=request.user)
    calories_percent = (totals["calories"] or 0) / user_profile.daily_calories * 100
    proteins_percent = (totals["proteins"] or 0) / user_profile.daily_proteins * 100
    fats_percent = (totals["fats"] or 0) / user_profile.daily_fats * 100
    carbs_percent = (totals["carbs"] or 0) / user_profile.daily_carbs * 100
    water_percent = record.water / user_profile.daily_water * 100

    labels, data_points, _ = get_weight_history_for_chart(
        request.user, limit=10, period="all", get_info=False
    )

    context = {
        "current_calories": totals["calories"] or 0,
        "current_proteins": totals["proteins"] or 0,
        "current_fats": totals["fats"] or 0,
        "current_carbs": totals["carbs"] or 0,
        "current_water": record.water,
        "current_weight": user_profile.weight,
        "daily_calories": user_profile.daily_calories,
        "daily_proteins": user_profile.daily_proteins,
        "daily_fats": user_profile.daily_fats,
        "daily_carbs": user_profile.daily_carbs,
        "daily_water": user_profile.daily_water,
        "breakfast_entries": breakfast_entries.order_by("date_added"),
        "lunch_entries": lunch_entries.order_by("date_added"),
        "dinner_entries": dinner_entries.order_by("date_added"),
        "snack_entries": snack_entries.order_by("date_added"),
        "calories_percent": calories_percent if calories_percent < 100 else 100,
        "proteins_percent": proteins_percent if proteins_percent < 100 else 100,
        "fats_percent": fats_percent if fats_percent < 100 else 100,
        "carbs_percent": carbs_percent if carbs_percent < 100 else 100,
        "water_percent": water_percent if water_percent < 100 else 100,
        "user_goal": user_profile.get_goal_display().lower(),
        "weight_data": {
            "labels": labels,
            "data": data_points,
        },
    }
    return render(request, "calculator_app/calculator.html", context)


@require_POST
@login_required
def add_water(request):
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        amount = json.loads(request.body).get("amount")

        if not isinstance(amount, (int, float)) or amount <= 0:
            return JsonResponse({"error": "Некорректное количество воды"}, status=400)

        user_timezone = request.session.get("user_timezone", "UTC")
        try:
            tz = ZoneInfo(user_timezone)
            today = timezone.now().astimezone(tz).date()
        except ZoneInfoNotFoundError:
            today = timezone.now().date()

        record, _ = UserDailyRecord.objects.get_or_create(
            user=request.user,
            user_date=today,
        )
        if (record.water + amount) > 10000:
            return JsonResponse(
                {"error": "Успокойтесь, вы выпили слишком много воды!"}, status=400
            )
        record.water += amount
        record.save()

        user_profile = get_object_or_404(UserProfile, user=request.user)

        water_percent = (record.water / user_profile.daily_water) * 100

        return JsonResponse(
            {
                "new_water": record.water,
                "water_percent": min(water_percent, 100),
            }
        )

    return JsonResponse({"error": "Недопустимый запрос"}, status=400)


@require_POST
@login_required
def update_weight(request):
    weight = request.POST.get("weight", 0)
    try:
        weight = float(weight)

        user_timezone = request.session.get("user_timezone", "UTC")
        try:
            tz = ZoneInfo(user_timezone)
            today = timezone.now().astimezone(tz).date()
        except ZoneInfoNotFoundError:
            today = timezone.now().date()

        record, _ = UserDailyRecord.objects.get_or_create(
            user=request.user,
            user_date=today,
        )

        record.weight = weight
        record.save()

        user_profile = get_object_or_404(UserProfile, user=request.user)
        user_profile.weight = weight
        user_profile.save()

    except ValueError:
        pass
    return redirect("calculator")


@require_POST
@login_required
def get_weight_history_graph(request):
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        period = json.loads(request.body).get("period")

        valid_periods = ["all", "week", "month", "year"]
        if period not in valid_periods:
            return JsonResponse(
                {"error": f"Некорректный период. Допустимые значения: {valid_periods}"},
                status=400,
            )

        labels, data_points, info = get_weight_history_for_chart(
            request.user, period=period, get_info=True
        )

        return JsonResponse(
            {
                "labels": labels,
                "data_points": data_points,
                "mean": info["mean"],
                "max": info["max"],
                "min": info["min"],
            }
        )

    return JsonResponse({"error": "Недопустимый запрос"}, status=400)


@login_required
def delete_entry(request, entry_id: int):
    entry = get_object_or_404(FoodEntry, id=entry_id, user=request.user)
    entry.delete()
    return redirect("calculator")


@login_required
def food_search(request, meal: str):
    query = request.GET.get("query", "")
    try:
        page = int(request.GET.get("page", 0))
    except ValueError:
        page = 0

    favorites = None

    if query:
        context = search_fatsecret_food(query, page=page, translate=False)
        context["meal"] = meal
        return render(request, "calculator_app/search_food.html", context)

    context = {"meal": meal, "favorites": favorites}
    return render(request, "calculator_app/search_food.html", context)


@login_required
def own_food_search(request, meal: str):
    query = request.GET.get("query", "")
    try:
        page = int(request.GET.get("page", 0))
    except ValueError:
        page = 0

    context = search_user_custom_food(user=request.user, query=query, page=page)
    context["meal"] = meal
    return render(request, "calculator_app/search_own_food.html", context)


@login_required
def favorite_food_search(request, meal: str):
    query = request.GET.get("query", "")
    try:
        page = int(request.GET.get("page", 0))
        max_result = int(request.GET.get("max", 5))
        max_result = 5 if max_result < 1 else max_result
    except ValueError:
        page = 0
        max_result = 5

    context = search_user_favorite_food(
        user=request.user, query=query, max_results=max_result, page=page
    )
    if page > 0 and not context.get("results", []):
        page -= 1
        context = search_user_favorite_food(
            user=request.user, query=query, max_results=max_result, page=page
        )

    context["meal"] = meal
    context["max_result"] = max_result
    return render(request, "calculator_app/search_favorite_food.html", context)


@login_required
def add_food_entry(request, food_id: str):
    is_food_custom = False

    next_url = request.GET.get("next", "calculator")

    if food_id.startswith("ucf"):
        is_food_custom = True
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
        return redirect(next_url)

    meal = request.GET.get("meal", "snack")
    if meal not in ["breakfast", "lunch", "dinner", "snack"]:
        meal = "snack"

    try:
        if food_id.startswith("ucf"):
            UserFavoriteCustomFood.objects.get(
                user=request.user, food_id=custom_food_id
            )
        else:
            food_id = int(food_id)
            UserFavoriteApiFood.objects.get(user=request.user, food_id=food_id)
        is_favorite = True
    except (ValueError, ObjectDoesNotExist):
        is_favorite = False

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
                food_name=food_details["food_name"],
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
        "is_custom": is_food_custom,
        "is_favorite": is_favorite,
        "next_url": next_url,
    }
    return render(request, "calculator_app/add_food_entry.html", context)


@login_required
def add_fast_entry(request):

    meal = request.GET.get("meal", "snack")
    if meal not in ["breakfast", "lunch", "dinner", "snack"]:
        meal = "snack"

    next_url = request.GET.get("next", reverse("calculator"))

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
        "next_url": next_url,
    }
    return render(request, "calculator_app/add_fast_entry.html", context)


@login_required
def create_custom_fodd(request):
    meal = request.GET.get("meal", "snack")
    if meal not in ["breakfast", "lunch", "dinner", "snack"]:
        meal = "snack"

    if request.method == "POST":
        form = UserCustomFoodForm(request.POST)
        if form.is_valid():
            custom_food = form.save(commit=False)
            custom_food.user = request.user
            custom_food.save()
            return redirect(reverse("own_food_search", kwargs={"meal": meal}))

    else:
        form = UserCustomFoodForm()

    context = {
        "form": form,
        "target": form.target if hasattr(form, "target") else "portion",
    }
    return render(request, "calculator_app/create_custom_food.html", context)


@login_required
def delete_custom_food(request, food_id: int):
    meal = request.GET.get("meal", "snack")
    if meal not in ["breakfast", "lunch", "dinner", "snack"]:
        meal = "snack"

    food = get_object_or_404(UserCustomFood, food_id=food_id, user=request.user)
    food.delete()
    return redirect(reverse("own_food_search", kwargs={"meal": meal}))


@login_required
def edit_custom_food(request, food_id: int):
    meal = request.GET.get("meal", "snack")
    if meal not in ["breakfast", "lunch", "dinner", "snack"]:
        meal = "snack"

    next_url = request.GET.get("next", "calculator")

    params = urlencode({"meal": meal, "next": next_url})

    food = get_object_or_404(UserCustomFood, user=request.user, food_id=food_id)

    if request.method == "POST":
        if "cancel" in request.POST:
            return redirect(
                f"{reverse('add_food_entry', kwargs={'food_id': "ucf" + str(food_id)})}?{params}"
            )

        form = UserCustomFoodForm(request.POST, instance=food)
        if form.is_valid():
            custom_food = form.save(commit=False)
            custom_food.user = request.user
            custom_food.save()
            return redirect(
                f"{reverse('add_food_entry', kwargs={'food_id': "ucf" + str(food_id)})}?{params}"
            )
    else:
        form = UserCustomFoodForm(instance=food)

    context = {
        "form": form,
        "target": form.target if hasattr(form, "target") else "portion",
    }
    return render(request, "calculator_app/edit_custom_food.html", context)


@login_required
@require_POST
def add_food_to_favorites(request, food_id: str):

    meal = request.GET.get("meal", "snack")
    if meal not in ["breakfast", "lunch", "dinner", "snack"]:
        meal = "snack"

    next_url = request.GET.get("next", "calculator")

    params = urlencode({"meal": meal, "next": next_url})

    brand_name = request.POST.get("brand_name", "").strip()
    if brand_name == "None":
        brand_name = None

    food_name = request.POST.get("food_name", "").strip()

    food_description = request.POST.get("food_description", "").strip()

    if food_id.startswith("ucf"):
        try:
            custom_food_id = int(food_id.replace("ucf", ""))
            custom_food = UserCustomFood.objects.get(
                food_id=custom_food_id, user=request.user
            )

            UserFavoriteCustomFood.objects.get_or_create(
                user=request.user,
                food=custom_food,
            )
        except (ValueError, UserCustomFood.DoesNotExist):
            pass
    else:
        try:
            if not food_name or not food_description:
                food_data = get_food_details(food_id)

                if food_data:
                    food_name = food_data["food_name"]
                    food_description = food_data["food_description"]

            UserFavoriteApiFood.objects.get_or_create(
                user=request.user,
                food_id=int(food_id),
                food_name=food_name,
                brand_name=brand_name,
                food_description=food_description,
            )
        except (ValueError, TypeError):
            pass

    return redirect(
        f"{reverse('add_food_entry', kwargs={'food_id': food_id})}?{params}"
    )


@login_required
@require_POST
def remove_food_from_favorites(request, food_id: str):

    referer = request.META.get("HTTP_REFERER")

    meal = request.GET.get("meal", "snack")
    if meal not in ["breakfast", "lunch", "dinner", "snack"]:
        meal = "snack"

    next_url = request.GET.get("next", "calculator")

    params = urlencode({"meal": meal, "next": next_url})

    if food_id.startswith("ucf"):
        try:
            custom_food_id = int(food_id.replace("ucf", ""))
            favorite = UserFavoriteCustomFood.objects.get(
                user=request.user, food_id=custom_food_id
            )
            favorite.delete()
        except (ValueError, UserFavoriteCustomFood.DoesNotExist):
            pass
    else:
        try:
            favorite = UserFavoriteApiFood.objects.get(
                user=request.user, food_id=int(food_id)
            )
            favorite.delete()
        except (ValueError, UserFavoriteApiFood.DoesNotExist):
            pass

    if referer:
        return redirect(referer)

    # Если referer не будет, то задаем redirect
    return redirect(
        f"{reverse('add_food_entry', kwargs={'food_id': food_id})}?{params}"
    )


@login_required
def food_image_recognition(request):

    prev_url = request.GET.get("prev", reverse("calculator"))

    meal = request.GET.get("meal", "snack")
    if meal not in ["breakfast", "lunch", "dinner", "snack"]:
        meal = "snack"

    context = {
        "prev_url": prev_url,
        "meal": meal,
    }

    FoodFormSet = formset_factory(ImageFoodEntryForm, extra=0)

    if request.method == "POST":
        files = request.FILES.getlist("image")
        # Если файлов нет, значит мы уже получили фото и сохраняем полученные данные
        if not files:
            formset = FoodFormSet(request.POST)
            if formset.is_valid():
                for form in formset:
                    # Создаем запись для каждой найденной и отмеченной еды
                    if form.cleaned_data["save_flag"]:
                        FoodEntry.objects.create(
                            user=request.user,
                            food_name=form.cleaned_data["food_name"],
                            amount=form.cleaned_data["amount"],
                            calories=round(form.cleaned_data["calories"]),
                            proteins=round(form.cleaned_data["proteins"], 1),
                            fats=round(form.cleaned_data["fats"], 1),
                            carbs=round(form.cleaned_data["carbs"], 1),
                            meal=meal,
                        )
                return redirect("calculator")
            else:
                upload_form = ImageUploadForm()
                context["upload_form"] = upload_form
                context["error"] = (
                    "Произошла ошибка при сохранении, попробуйте ещё раз."
                )
        # Если файлы есть, то проверяем, что это фото
        else:
            upload_form = ImageUploadForm(request.POST, request.FILES)
            if upload_form.is_valid():
                image = upload_form.cleaned_data["image"]

                tmp_path = default_storage.save(f"tmp/{image.name}", image)
                full_path = default_storage.path(tmp_path)

                result, base64_image = get_products_from_image(full_path)

                default_storage.delete(tmp_path)

                if result and result.get("is_food_was_found", False):
                    initial_data = []
                    try:
                        total_calories = 0
                        total_proteins = 0
                        total_fats = 0
                        total_carbs = 0
                        for food in result.get("foods", []):
                            calories = int(food.get("calories"))
                            proteins = round(float(food.get("proteins")), 1)
                            fats = round(float(food.get("fats")), 1)
                            carbs = round(float(food.get("carbs")), 1)

                            total_calories += calories
                            total_proteins += proteins
                            total_fats += fats
                            total_carbs += carbs

                            initial_data.append(
                                {
                                    "food_name": str(food.get("food_name")),
                                    "amount": str(food.get("amount")),
                                    "calories": calories,
                                    "proteins": proteins,
                                    "fats": fats,
                                    "carbs": carbs,
                                    "meal": meal,
                                }
                            )

                            context["formset"] = FoodFormSet(initial=initial_data)
                            context["total"] = {
                                "total_products": result.get(
                                    "count", len(result["foods"])
                                ),
                                "total_calories": total_calories,
                                "total_proteins": total_proteins,
                                "total_fats": total_fats,
                                "total_carbs": total_carbs,
                            }
                            context["image_data"] = base64_image

                    except (AttributeError, ValueError, TypeError):
                        context["error"] = (
                            "Произошла ошибка при получении ответа, повторите отправку снова.."
                        )
                        context["upload_form"] = upload_form
                else:
                    context["error"] = "Продукты на изображении не найдены!"
                    context["upload_form"] = upload_form

            else:
                context["error"] = (
                    "Не удалось открыть файл с изображением! Попробуйте другое изображение."
                )
                context["upload_form"] = upload_form
    else:
        upload_form = ImageUploadForm()
        context["upload_form"] = upload_form
        context["show_hello"] = True

    return render(
        request,
        "calculator_app/food_recognition.html",
        context,
    )


@login_required
def barcode_image_scanning(request):

    prev_url = request.GET.get("prev", reverse("calculator"))

    meal = request.GET.get("meal", "snack")
    if meal not in ["breakfast", "lunch", "dinner", "snack"]:
        meal = "snack"

    context = {
        "prev_url": prev_url,
        "meal": meal,
    }

    decoded_text = None
    manual_code = None
    product_data = None

    if request.method == 'POST':
        form = BarcodeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            manual_code = form.cleaned_data.get('manual_code')
            image_file = form.cleaned_data.get('image')

            if image_file:
                image = Image.open(image_file)
                decoded_objects = decode(image)
                if decoded_objects:
                    decoded_text = decoded_objects[0].data.decode('utf-8').strip()

            final_code = decoded_text or manual_code
            if final_code:
                product_data = get_product_by_barcode(final_code)
            
            context["code"] = final_code
            context["result"] = product_data
            context["add_form"] = True

    else:
        upload_form = BarcodeUploadForm()
        context["upload_form"] = upload_form
        context["show_hello"] = True

    return render(
        request,
        "calculator_app/barcode_scanning.html",
        context,
    )