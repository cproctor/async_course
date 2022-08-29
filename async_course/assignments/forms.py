from django import forms
from assignments.models import Assignment, Submission, check_mime_type
import magic

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = [
            'due_date', 
            'title', 
            'slug', 
            'markdown', 
            'due_date', 
            'active', 
            'has_submissions', 
            'peer_review'
        ]

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['upload']

    def clean_upload(self):
        upload = self.cleaned_data['upload']
        mimetype = magic.from_buffer(upload.file.read(2048), mime=True)
        check_mime_type(mimetype)
        return upload
