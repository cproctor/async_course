from django.db import models
from pubref.models import PandocMarkdownModel
from django.contrib.auth.models import User

class Profile(PandocMarkdownModel):

    class EmailFrequency(models.TextChoices):
        DAILY = "DAILY"
        WEEKLY = "WEEKLY"
        NEVER = "NEVER"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    email_frequency = models.CharField(max_length=20, choices=EmailFrequency.choices, 
            default=EmailFrequency.WEEKLY)

    def grade(self):
        """Calculates the student's grade"""
        return "Pass"

