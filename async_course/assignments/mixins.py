from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from assignments.models import Assignment, Submission
from django.contrib.auth.models import User
from reviews.models import ReviewerRole
from django.shortcuts import redirect
from reviews.forms import ReviewForm, AuthoritativeReviewForm

class AssignmentSubmissionsMixin:
    """A mixin for the assignment submissions page. 
    Controls access, sets instance properties, and populates template context.
    """

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('login')
        self.look_up_context_objects()
        return super().dispatch(request, *args, **kwargs)

    def look_up_context_objects(self):
        try:
            self.assignment = Assignment.objects.get(slug=self.kwargs['slug'])
            students = User.objects.filter(profile__is_student=True)
            self.author = students.get(username=self.kwargs['username'])
            self.reviewer_role = ReviewerRole.objects.get(
                reviewer=self.request.user,
                reviewed=self.author,
                assignment=self.assignment,
            )
        except (
            Assignment.DoesNotExist, 
            User.DoesNotExist, 
            Submission.DoesNotExist,
            ReviewerRole.DoesNotExist,
        ):
            raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignment'] = self.assignment
        context['submissions'] = self.get_queryset().all()
        context['author'] = self.author
        context['status'] = self.assignment.get_status(self.author)
        context['new_review_form'] = self.get_review_form_class()()
        return context

    def get_review_form_class(self):
        if self.reviewer_role.authoritative:
            return AuthoritativeReviewForm
        else:
            return ReviewForm

class AssignmentSubmissionVersionMixin(AssignmentSubmissionsMixin):
    """A mixin for interacting with a specific assignment version.
    """

    def look_up_context_objects(self):
        super().look_up_context_objects()
        self.submission = Submission.objects.get(
            assignment=self.assignment,
            author=self.author, 
            version=self.kwargs['version']
        )

