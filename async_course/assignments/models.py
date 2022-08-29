from pubref.models import PandocMarkdownModel
from django.db import models
from django.conf import settings
from os.path import splitext
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db.models import Q

class Assignment(PandocMarkdownModel):
    due_date = models.DateTimeField(null=True, blank=True)
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=40, unique=True)
    active = models.BooleanField(default=False)
    has_submissions = models.BooleanField(default=True)
    peer_review = models.BooleanField(default=False)

    assignment_statuses = ['NOT_STARTED', 'STARTED', 'COMPLETE']
    def get_status(self, user):
        """Returns the user's status for the current assignemnt.
        """
        submissions = self.submissions.filter(author=user)
        if submissions.filter(reviews__accepted=True).exists():
            return 'COMPLETE'
        elif submissions.exists():
            return 'STARTED'
        else:
            return 'NOT_STARTED'

    def get_absolute_url(self):
        return reverse_lazy('assignments:detail', args=[self.slug])

    class Meta:
        ordering = ['due_date']

class AssignmentExample(models.Model):
    description = models.TextField(null=True, blank=True)
    assignment = models.ForeignKey(Assignment, related_name="examples",
            on_delete=models.CASCADE)
    upload = models.FileField(upload_to="examples/")
    mime = models.CharField(max_length=100, default="application/pdf")

    class Meta:
        ordering = ['description']

def upload_filename(instance, original_filename):
    """Defines the filename where the file will be saved, like proctor_
    """
    author = instance.author.last_name
    assignment = instance.assignment.slug
    version = f"v{instance.version}"
    stem, suffix = splitext(original_filename)
    return '_'.join([
        settings.MEDIA_PREFIX,
        assignment,
        author,
        version
    ]) + suffix

check_file_extension = FileExtensionValidator(
        allowed_extensions=settings.UPLOAD_ALLOWED_EXTENSIONS)

def check_file_size(value):
    if value.size > settings.UPLOAD_MAX_SIZE:
        raise ValidationError("File is too large")

def check_mime_type(value):
    mime = settings.UPLOAD_ALLOWED_MIME_TYPES
    if not (mime == '*' or value in mime):
        raise ValidationError("Unsupported file type")

class Submission(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    assignment = models.ForeignKey(Assignment, related_name="submissions",
            on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name="submissions", 
            on_delete=models.CASCADE)
    version = models.IntegerField()
    upload = models.FileField(upload_to=upload_filename, 
            validators=[check_file_extension, check_file_size])
    mime = models.CharField(max_length=200, validators=[check_mime_type])
    shared = models.BooleanField(default=False)

    def interested_people(self):
        return User.objects.filter(
            Q(reviewer_roles__assignment=self.assignment) | 
            Q(reviewed_roles__assignment=self.assignment)
        ).all()

    @classmethod
    def get_next_version(cls, author, assignment):
        """Returns the next version number for the author and assignment.
        """
        return Submission.objects.filter(author=author, assignment=assignment).count()

