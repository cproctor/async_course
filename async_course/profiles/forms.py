from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.models import User
from profiles.models import Profile

class ProfileForm(forms.Form):
    first_name = forms.CharField(min_length=1)
    last_name = forms.CharField(min_length=1)
    username = forms.CharField(min_length=2, max_length=30)
    email_frequency = forms.CharField(label='Email frequency', 
            widget=forms.RadioSelect(choices=Profile.EmailFrequency.choices))
    markdown = forms.CharField(label='Profile text', 
            widget=forms.Textarea, required=False)

    def __init__(self, data, user):
        super().__init__(data)
        self.user = user

    def clean_username(self):
        new_username = self.cleaned_data['username']
        new_username_exists = User.objects.filter(username=new_username).exists()
        if new_username != self.user.username and new_username_exists:
            raise ValidationError(f"The username {value} is already being used.")
        return new_username


