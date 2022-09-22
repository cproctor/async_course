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
    
    class Status(models.TextChoices):
        NOT_STARTED = '0', "Not started"
        WAITING_FOR_REVIEW = '1', "Waiting for review"
        WAITING_FOR_TEACHER_REVIEW = '4', "Waiting for teacher review"
        WAITING_FOR_SUBMISSION = '2', "Waiting for new submission"
        COMPLETE = '3', "Complete"

    status = models.CharField(max_length=1, choices=Status.choices, default=Status.NOT_STARTED)

    def __str__(self):
        return "{} reviewing {}'s {} ({})".format(
            self.reviewer.username,
            self.reviewed.username,
            self.assignment.title,
            self.get_status()
        )

    def get_status(self):
        subs = self.assignment.submissions.filter(author=self.reviewed)
        if not subs.exists():
            return self.Status.NOT_STARTED
        elif subs.filter(reviews__accepted=True):
            return self.Status.COMPLETE
        else:
            rrs = self.adjacent(authoritative=True)
            auth_reviews = sum([list(rr.reviews.all()) for rr in rrs], [])
            if auth_reviews:
                return self.Status.WAITING_FOR_SUBMISSION
            else:
                last_submission_date = subs.last().date_created
                last_review_date = self.reviews.last().date_created
                if last_submission_date > last_review_date:
                    return self.Status.WAITING_FOR_REVIEW
                else:
                    return self.Status.WAITING_FOR_TEACHER_REVIEW

    def adjacent(self, authoritative=False):
        "Returns reviewer_roles having the same assignment and reviewed"
        qs = ReviewerRole.objects.filter(
                assignment=self.assignment, reviewed=self.reviewed)
        if authoritative:
            qs = qs.filter(authoritative=True)
        return qs

class Review(PandocMarkdownModel):
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    submission = models.ForeignKey("assignments.Submission", related_name="reviews", 
            on_delete=models.CASCADE)
    reviewer_role = models.ForeignKey(ReviewerRole, related_name="reviews",
            on_delete=models.CASCADE, null=True)
    accepted = models.BooleanField(default=False, null=True)

    def interested_people(self):
        people = set()
        for role in self.reviewer_role.adjacent():
            people.add(role.reviewer)
            people.add(role.reviewed)
        return people

    class Meta:
        ordering = ['date_created']

