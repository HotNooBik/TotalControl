from pprint import pprint

import requests

from django.conf import settings

from calculator_app.services import prepare_image

from .prompts import MODEL_VERSION, get_prompt


def get_answer(user, prompt: str, image_path: str | None = None):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEYS[0]}",
        "Content-Type": "application/json",
    }

    messages = [
        {"role": "user", "content": [{"type": "text", "text": get_prompt(user) + prompt + '"""'}]},
    ]

    if image_path:
        base64_image = prepare_image(image_path)
        if base64_image:
            data_url = f"data:image/jpeg;base64,{base64_image}"
            messages[0]["content"].append(
                {"type": "image_url", "image_url": {"url": data_url}}
            )

    payload = {"model": MODEL_VERSION, "messages": messages}

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    keys_count = len(settings.OPENROUTER_API_KEYS) - 1
    while response.json().get("error", {}).get("code", 0) == 429 and keys_count > 0:
        headers["Authorization"] = f"Bearer {settings.OPENROUTER_API_KEYS[keys_count]}"
        keys_count -= 1
        response = requests.post(url, headers=headers, json=payload, timeout=60)

    answer = (
        response.json().get("choices", [{}])[0].get("message", {}).get("content", None)
    )

    if not answer:
        return None
    return answer
