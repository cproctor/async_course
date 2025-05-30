from django import forms
from .models import Page

class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ['menu_label', 'slug', 'markdown', 'in_menu', 'weight']
