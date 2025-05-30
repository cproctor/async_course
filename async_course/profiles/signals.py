from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from profiles.models import Profile

@receiver(post_save, sender=User, dispatch_uid="create_profile_after_user_creation")
def create_profile_after_user_signup(sender, **kwargs):
    "When a user is created, create a profile"
    user = kwargs['instance']
    if kwargs['created']:
        Profile.objects.create(user=user)
