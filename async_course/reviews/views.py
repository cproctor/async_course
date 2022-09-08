from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, FormView, DeleteView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from profiles.mixins import AuthorOrTeacherRequiredMixin
from assignments.mixins import AssignmentSubmissionVersionMixin
from reviews.forms import ReviewForm, AuthoritativeReviewForm
from reviews.models import Review, ReviewerRole
from django.contrib.auth.mixins import LoginRequiredMixin
from events.models import Event
from analytics.mixins import AnalyticsMixin
from reviews.email import notify_author_of_new_review

class ListReviews(LoginRequiredMixin, AnalyticsMixin, ListView):

    def get_queryset(self):
        return ReviewerRole.objects.filter(reviewer=self.request.user).exclude(
                reviewed=self.request.user)

    def get_context_data(self, *args, **kwargs):
        roles = self.get_queryset()
        context = super().get_context_data(*args, **kwargs)
        context['roles'] = [r for r in self.get_queryset() if r.get_status() != 'NOT_STARTED']
        return context

class NewReview(AssignmentSubmissionVersionMixin, AnalyticsMixin, FormView):
    def post(self, *args, **kwargs):
        form = self.get_review_form_class()(self.request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer_role = self.reviewer_role
            review.submission = self.submission
            if not self.reviewer_role.authoritative:
                review.accepted=False
            review.compile_markdown()
            review.save()
            notify_author_of_new_review(review)
            evt = Event(user=self.author, action=Event.EventActions.ADDED_REVIEW, 
                    object_id=review.id)
            evt.save()
            for user in review.interested_people():
                evt.notifications.create(user=user)
            return redirect('assignments:submissions', slug=self.assignment.slug,
                    username=self.author.username)
        else:
            context = {}
            context['assignment'] = self.assignment
            context['submissions'] = self.assignment.submissions.filter(author=self.author).all()
            context['author'] = self.author
            context['status'] = self.assignment.get_status(self.author)
        return context

class EditReview(AuthorOrTeacherRequiredMixin, AnalyticsMixin, UpdateView):
    model = Review
    template_name = "reviews/review_form.html"

    def get_form_class(self):
        if self.get_object().reviewer_role.authoritative:
            return AuthoritativeReviewForm
        else:
            return ReviewForm

    def post(self, *args, **kwargs):
        form = self.get_form_class()(self.request.POST, instance=self.get_object())
        if form.is_valid():
            review = form.save(commit=False)
            review.compile_markdown()
            review.save()
            return redirect(self.get_success_url())
        else:
            context = self.get_context_data()
            context['form'] = form
            return render(self.request, self.template_name, context)

    def get_object_author(self):
        return self.get_object().reviewer_role.reviewer

    def get_success_url(self):
        return reverse_lazy('assignments:submissions', args=[
            self.get_object().reviewer_role.assignment.slug,
            self.get_object().reviewer_role.reviewed
        ])

class DeleteReview(AuthorOrTeacherRequiredMixin, AnalyticsMixin, DeleteView):
    pass
