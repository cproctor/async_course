from django.db import models
from django.contrib.auth.models import User
from pubref.models import PandocMarkdownModel
from assignments.models import Assignment
from django.db.models import Q

class ReviewerRole(models.Model):
    reviewer = models.ForeignKey(User, related_name="reviewer_roles", 
            on_delete=models.CASCADE)
    reviewed = models.ForeignKey(User, related_name="reviewed_roles",
            on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, related_name="reviewer_roles",
            on_delete=models.CASCADE, null=True)
    authoritative = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    reviewer_role_statuses = [
        'NOT_STARTED', 
        'WAITING_FOR_REVIEW', 
        'WAITING_FOR_SUBMISSION', 
        'COMPLETE'
    ]

    def __str__(self):
        return "{} reviewing {}'s {} ({})".format(
            self.reviewer.username,
            self.reviewed.username,
            self.assignment.title,
            self.get_status()
        )

    def get_status(self):
        subs = self.assignment.submissions.filter(author=self.reviewed)
        if subs.filter(reviews__accepted=True):
            return 'COMPLETE'
        elif not subs.exists():
            return 'NOT_STARTED'
        else:
            if not self.reviews.exists():
                return 'WAITING_FOR_REVIEW'
            last_submission_date = subs.last().date_created
            last_review_date = self.reviews.last().date_created
            if last_submission_date > last_review_date:
                return 'WAITING_FOR_REVIEW'
            else:
                return 'WAITING_FOR_SUBMISSION'

class Review(PandocMarkdownModel):
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    submission = models.ForeignKey("assignments.Submission", related_name="reviews", 
            on_delete=models.CASCADE)
    reviewer_role = models.ForeignKey(ReviewerRole, related_name="reviews",
            on_delete=models.CASCADE, null=True)
    accepted = models.BooleanField(default=False, null=True)

    def interested_people(self):
        assn = self.reviewer_role.assignment
        return User.objects.filter(
            Q(reviewer_roles__assignment=assn) | 
            Q(reviewed_roles__assignment=assn)
        ).all()

    class Meta:
        ordering = ['date_created']

