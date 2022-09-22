from django import template
from reviews.models import ReviewerRole, Review
from assignments.models import Assignment
from events.models import Event, Notification

register = template.Library()

@register.simple_tag
def reviews_needing_action_count(user):
    if not user.is_authenticated:
        return 0
    return user.reviewer_roles.filter(status=ReviewerRole.Status.WAITING_FOR_REVIEW).count()

@register.simple_tag
def assignments_with_unseen_reviews(user):
    if not user.is_authenticated or user.profile.is_teacher:
        return 0
    review_ids = [r.id for r in Review.objects.filter(submission__author=user)]
    notifications = Notification.objects.filter(
        user=user,
        read=False,
        event__action=Event.EventActions.ADDED_REVIEW,
        event__object_id__in=review_ids
    ).select_related('event')
    review_ids = set([n.event.object_id for n in notifications])
    assns =  Assignment.objects.filter(reviewer_roles__reviews__in=review_ids).distinct().count()
    return assns

