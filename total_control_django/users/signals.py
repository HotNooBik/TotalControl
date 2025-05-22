from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from .models import UserProfile, UserDailyRecord


# ------------------------- Под удаление ------------------------
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.create(user=instance)
#
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.userprofile.save()
#----------------------------------------------------------------


@receiver(pre_save, sender=UserDailyRecord)
def on_create_daily_record(sender, instance, **kwargs):
    if instance.pk is None:    # Срабатывает, если объекта ещё нет в базе
        profile = UserProfile.objects.get(user=instance.user)
        instance.weight = profile.weight
        instance.calories_goal = profile.daily_calories
        instance.proteins_goal = profile.daily_proteins
        instance.fats_goal = profile.daily_fats
        instance.carbs_goal = profile.daily_carbs
        instance.water_goal = profile.daily_water
