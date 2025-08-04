from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance,
            age=25,
            gender='male',
            height=170,
            current_weight=70,
            target_weight=60,
            activity_level='moderate'
        )
