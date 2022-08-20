from django import forms
from .models import Assignment

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['due_date', 'title', 'slug', 'active', 'peer_review', 'markdown']
