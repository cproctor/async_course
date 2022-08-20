from django import template
from pages.models import Page

register = template.Library()

@register.simple_tag
def pages_in_menu():
    return Page.objects.filter(in_menu=True).all()
