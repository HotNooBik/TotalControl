from pprint import pprint
import base64
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from PIL import Image

from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages as dj_messages

from users.models import UserProfile

from calculator_app.services import prepare_image

from .services import get_answer
from .models import Message


@login_required
def chat_assistant(request):
    if request.method == "POST":
        if "clear" in request.POST:
            Message.objects.filter(user=request.user).delete()
            return redirect("chat")

        user_message = request.POST.get("message", "").strip()

        if not user_message:
            return redirect("chat")

        image_file = request.FILES.get("image")
        full_img_path = None
        image_bytes = None
        tmp_path = None

        if image_file:
            try:
                if image_file.size > 5 * 1024 * 1024:
                    dj_messages.error(
                        request, "Изображение слишком большое (макс. 5MB)."
                    )
                    return redirect("chat")

                image = Image.open(image_file)
                image.verify()
                tmp_path = default_storage.save(f"tmp/{image_file.name}", image_file)
                full_img_path = default_storage.path(tmp_path)

                base64_image = prepare_image(full_img_path, max_size=200)
                if base64_image:
                    image_bytes = base64.b64decode(base64_image)

            except Exception as error:
                print(error)
                return redirect("chat")

        Message.objects.create(
            user=request.user,
            role="user",
            content=user_message,
            image_data=image_bytes,
        )

        bot_response = get_answer(request.user, user_message, image_path=full_img_path)

        if not bot_response:
            bot_response = "Сервис временно не доступен. Повторите попытку позже."

        if tmp_path and default_storage.exists(tmp_path):
            default_storage.delete(tmp_path)

        Message.objects.create(
            user=request.user, role="assistant", content=bot_response
        )

        return redirect("chat")

    user_profile = get_object_or_404(UserProfile, user=request.user)
    try:
        tz = ZoneInfo(user_profile.timezone)
    except ZoneInfoNotFoundError:
        tz = timezone.get_current_timezone()
    timezone.activate(tz)

    messages = Message.objects.filter(user=request.user).order_by("date_sent")[:20]

    for msg in messages:
        msg.image_data = msg.get_image_base64()

    if not messages.exists():
        start_msg = """
###Здравствуйте! 
Я ваш помощник по **питанию** и **здоровому образу жизни**. Чем могу помочь: планирование рациона, подбор тренировок или что-то ещё?
"""
        Message.objects.create(
            user=request.user,
            role="assistant",
            content=start_msg,
            date_sent=timezone.now(),
        )
        messages = Message.objects.filter(user=request.user).order_by("date_sent")[:20]

    context = {"messages": messages}

    return render(request, "chat_assistant/chat.html", context)
