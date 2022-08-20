from django import template

register = template.Library()

@register.simple_tag
def did_upvote(user, post):
    return post.upvotes.filter(voter=user).exists()
