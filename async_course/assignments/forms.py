from django import forms
from assignments.models import Assignment, Submission, check_mime_type
import magic

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['due_date', 'title', 'slug', 'active', 'peer_review', 'markdown']

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['upload']

    def clean_upload(self):
        upload = self.cleaned_data['upload']
        mimetype = magic.from_file(upload.file, mime=True)
        check_mime_type(mimetype)
