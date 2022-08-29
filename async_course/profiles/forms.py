from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.models import User
from profiles.models import Profile

class ProfileForm(forms.Form):
    first_name = forms.CharField(min_length=1)
    last_name = forms.CharField(min_length=1)
    email_frequency = forms.CharField(label='Email frequency', 
            widget=forms.RadioSelect(choices=Profile.EmailFrequency.choices))
    markdown = forms.CharField(label='Profile text', 
            widget=forms.Textarea, required=False)

    def __init__(self, data, user):
        super().__init__(data)
        self.user = user
