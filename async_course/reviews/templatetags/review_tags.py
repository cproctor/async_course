from django import template
from reviews.models import ReviewerRole

register = template.Library()

@register.simple_tag
def reviews_needing_action_count(user):
    if not user.is_authenticated:
        return 0
    return user.reviewer_roles.filter(status=ReviewerRole.Status.WAITING_FOR_REVIEW).count()
