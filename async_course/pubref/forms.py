from django import forms
from pybtex.style.template import FieldIsMissing
from .models import Publication

class AddPublicationsForm(forms.Form):
    bibtex = forms.CharField(widget=forms.Textarea)

class EditPublicationForm(forms.Form):
    bibtex = forms.CharField(widget=forms.Textarea)

    def clean_bibtex(self):
        temp_pub = Publication(slug="slug", bibtex=self.cleaned_data["bibtex"])
        try:
            temp_pub.get_apa_html()
        except FieldIsMissing as e:
            raise forms.ValidationError(str(e))
