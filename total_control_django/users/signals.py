from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile, UserDailyRecord


# Под удаление
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.create(user=instance)
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.userprofile.save()


@receiver(pre_save, sender=UserDailyRecord)
def set_default_weight(sender, instance, **kwargs):
    if instance.weight is None:
        try:
            profile = UserProfile.objects.get(user=instance.user)
            instance.weight = profile.weight
        except UserProfile.DoesNotExist:
            pass
