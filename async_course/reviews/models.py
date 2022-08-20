from django.db import models
from django.contrib.auth.models import User
from pubref.models import PandocMarkdownModel

class ReviewerRole(models.Model):
    reviewer = models.ForeignKey(User, related_name="reviewer_roles", 
            on_delete=models.CASCADE)
    reviewed = models.ForeignKey(User, related_name="reviewed_roles",
            on_delete=models.CASCADE)
    authoritative = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

class Review(PandocMarkdownModel):
    submission = models.ForeignKey("assignments.Submission", related_name="reviews", 
            on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False, null=True)
