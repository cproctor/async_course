from django.db import models
from pubref.models import PandocMarkdownModel
from django.contrib.auth.models import User

class Profile(PandocMarkdownModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)

    def grade(self):
        """Calculates the student's grade"""
        return "Pass"
