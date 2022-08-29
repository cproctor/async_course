from django import template

register = template.Library()

@register.simple_tag
def reviews_needing_action_count(user):
    if not user.is_authenticated:
        return 0
    rrs = user.reviewer_roles.all()
    return len([rr for rr in rrs if rr.get_status() == 'WAITING_FOR_REVIEW'])
