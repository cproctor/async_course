from django import forms
from .models import Page

class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ['in_menu', 'menu_label', 'slug', 'markdown']
