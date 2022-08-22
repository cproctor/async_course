from django import forms
from django.core.exceptions import ValidationError
from pybtex.style.template import FieldIsMissing
from .models import Publication

class AddPublicationsForm(forms.Form):
    bibtex = forms.CharField(widget=forms.Textarea)

class EditPublicationForm(forms.ModelForm):

    def clean_bibtex(self):
        temp_pub = Publication(slug="slug", bibtex=self.cleaned_data["bibtex"])
        try:
            temp_pub.get_apa()
            return self.cleaned_data["bibtex"]
        except FieldIsMissing as e:
            raise ValidationError(str(e))

    class Meta:
        model = Publication
        fields = ['bibtex']
        widgets = {'bibtex': forms.Textarea}
