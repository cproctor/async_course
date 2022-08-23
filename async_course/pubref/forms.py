from django import forms
from django.core.exceptions import ValidationError
from pybtex.style.template import FieldIsMissing
from pybtex.exceptions import PybtexError
from .models import Publication

class AddPublicationsForm(forms.Form):
    bibtex = forms.CharField(widget=forms.Textarea)

class EditPublicationForm(forms.ModelForm):

    def clean_bibtex(self):
        temp_pub = Publication(slug="slug", bibtex=self.cleaned_data["bibtex"])
        try:
            temp_pub.get_apa()
            temp_pub.get_slug_from_bibtex()
            return self.cleaned_data["bibtex"]
        except (PybtexError, Publication.InvalidBibtex) as e:
            raise ValidationError("The bibtex must contain a single entry.")

    class Meta:
        model = Publication
        fields = ['bibtex']
        widgets = {'bibtex': forms.Textarea}
