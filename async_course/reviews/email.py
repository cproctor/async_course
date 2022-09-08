from common.email import send_email
from django.urls import reverse_lazy
from reviews.models import ReviewerRole

NEW_REVIEW = """Dear {},

A new review has been posted of your {} submission. You can read the review at {}.
"""
NEW_SUBMISSION = """Dear {},

{} {} has uploaded a new submission for {}. You are assigned as a reviewer on this submission. Please view the submission at {} and provide feedback within three school days. Thanks!
"""

def notify_author_of_new_review(review):
    """Sends and logs email to an author when there is a new review.
    """
    author = review.submission.author
    if author.email:
        url = reverse_lazy('assignments:submissions', args=[
            review.reviewer_role.assignment.slug,
            review.reviewer_role.reviewed
        ])
        send_email(
            f"New review of your {review.submission.assignment.title} submission",
            NEW_REVIEW.format(author.first_name, review.submission.assignment.title, url),
            [author.email]
        )

def notify_reviewers_of_new_submission(submission):
    author = submission.author
    assignment = submission.assignment
    url = reverse_lazy('assignments:submissions', args=[
        assignment.slug,
        author.username,
    ])
    roles = ReviewerRole.objects.filter(reviewed=author, assignment=assignment, 
            active=True).exclude(reviewer=author).all()
    for role in roles:
        reviewer = role.reviewer
        if reviewer.email:
            send_email(
                f"Your review needed for a {assignment.title} submission",
                NEW_SUBMISSION.format(
                    reviewer.first_name, 
                    author.first_name, 
                    author.last_name, 
                    assignment.title,
                    url,
                ),
                [reviewer.email]
            )


