import base64

from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()


class Message(models.Model):
    ROLE_CHOICES = [
        ("user", "Пользователь"),
        ("assistant", "ИИ"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    image_data = models.BinaryField(blank=True, null=True)
    date_sent = models.DateTimeField(auto_now_add=True)

    def get_image_base64(self):
        if self.image_data:
            encoded = base64.b64encode(self.image_data).decode("utf-8")
            return f"data:image/jpeg;base64,{encoded}"
        return None
