from django import template
from events.models import Event

register = template.Library()

@register.simple_tag
def did_upvote(user, post):
    return post.upvotes.filter(voter=user).exists()

@register.simple_tag
def unseen_posts_count(user):
    if not user.is_authenticated: 
        return 0
    return user.notifications.filter(
            read=False, event__action=Event.EventActions.CREATED_POST).count()
