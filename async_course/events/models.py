from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):

    class EventActions(models.TextChoices):
        CREATED_POST = "CREATED_POST"
        ADDED_SUBMISSION = "ADDED_SUBMISSION"
        ADDED_REVIEW = "ADDED_REVIEW"

    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=EventActions.choices)
    object_id = models.IntegerField()

    class Meta:
        ordering = ['date']

class Notification(models.Model):
    event = models.ForeignKey(Event, related_name="notifications",
            on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="notifications", 
            on_delete=models.CASCADE)
    read = models.BooleanField(default=False)
