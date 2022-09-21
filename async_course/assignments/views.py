from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, FormView, FormMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from profiles.mixins import TeacherRequiredMixin
from assignments.models import Assignment, Submission, AssignmentExample
from assignments.forms import AssignmentForm, SubmissionForm
from assignments.mixins import AssignmentSubmissionsMixin, AssignmentSubmissionVersionMixin
from reviews.models import ReviewerRole
import magic
from pathlib import Path
from events.models import Event, Notification
from analytics.mixins import AnalyticsMixin
from reviews.email import notify_reviewers_of_new_submission

def has_unseen_reviews(assignment, user):
    "Returns whether the user has unread review notifications for the assignment"
    reviewer_roles = ReviewerRole.objects.filter(
        assignment=assignment, reviewed=user
    ).prefetch_related('reviews')
    review_ids = set()
    for role in reviewer_roles:
        for review in role.reviews.all():
            review_ids.add(review.id)
    return user.notifications.filter(
        read=False, 
        event__action=Event.EventActions.ADDED_REVIEW,
        event__object_id__in=review_ids,
    ).exists()

class ListAssignments(AnalyticsMixin, LoginRequiredMixin, ListView):
    queryset = Assignment.objects.filter(active=True)
    context_object_name = "assignments"

    def get_context_data(self, **kwargs):
        assignments = Assignment.objects.all()
        u = self.request.user
        aws = [[has_unseen_reviews(a, u), a.get_status(u), a] for a in assignments]
        context = super().get_context_data(**kwargs)
        context['assignments_with_status'] = aws
        return context

class NewAssignment(AnalyticsMixin, TeacherRequiredMixin, CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = "assignments/assignment_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["prompt"] = "New assignment"
        context['url'] = reverse_lazy("assignments:new")
        return context

    def post(self, *args, **kwargs):
        form = AssignmentForm(self.request.POST)
        if form.is_valid():
            assn = form.save(commit=False)
            assn.compile_markdown()
            assn.save()
            return redirect("assignments:detail", slug=assn.slug)
        else:
            context = self.get_context_data()
            context["form"] = form
            return render(self.request, self.template_name, context)

class EditAssignment(AnalyticsMixin, TeacherRequiredMixin, UpdateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = "assignments/assignment_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["prompt"] = "Edit assignment"
        context['url'] = reverse_lazy("assignments:edit", args=[self.get_object().slug])
        return context

    def post(self, *args, **kwargs):
        form = AssignmentForm(self.request.POST, instance=self.get_object())
        if form.is_valid():
            assn = form.save(commit=False)
            assn.compile_markdown()
            assn.save()
            return redirect("assignments:detail", slug=assn.slug)
        else:
            context = self.get_context_data()
            context["form"] = form
            return render(self.request, self.template_name, context)

class ShowAssignment(AnalyticsMixin, LoginRequiredMixin, DetailView):
    model = Assignment

class ShowAssignmentRoster(AnalyticsMixin, DetailView):
    queryset = Assignment.objects.filter(has_submissions=True)
    template_name = "assignments/assignment_roster.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        students = User.objects.filter(profile__is_student=True).all()
        context['roster'] = [[u, self.object.get_status(u)] for u in students]
        return context

class ShowAssignmentSubmissions(AnalyticsMixin, AssignmentSubmissionsMixin, FormMixin, ListView):
    form_class = SubmissionForm

    def dispatch(self, *args, **kwargs):
        self.look_up_context_objects()
        self.object_list = self.get_queryset().all()
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return Submission.objects.filter(
            assignment=self.assignment, author=self.author
        ).prefetch_related('reviews', 'reviews__reviewer_role')

    def get(self, *args, **kwargs):
        review_ids = []
        for rr in self.reviewer_role.adjacent():
            review_ids += [r.id for r in rr.reviews.all()]
        print("REVIEW IDS", review_ids)
        self.request.user.notifications.filter(
            event__action=Event.EventActions.ADDED_REVIEW,
            event__object_id__in=review_ids,
            read=False,
        ).update(read=True)
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        form = self.form_class(self.request.POST, self.request.FILES)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.assignment = self.assignment
            sub.author = self.author
            sub.version = Submission.get_next_version(self.author, self.assignment)
            sub.mime = magic.from_buffer(sub.upload.file.read(2048), mime=True)
            sub.save()
            for rr in ReviewerRole.objects.filter(
                assignment=sub.assignment,
                reviewed=sub.author,
            ):
                rr.status = rr.get_status()
                rr.save()
            notify_reviewers_of_new_submission(sub)
            evt = Event(user=self.author, action=Event.EventActions.ADDED_SUBMISSION, 
                    object_id=sub.id)
            evt.save()
            for user in sub.interested_people():
                evt.notifications.get_or_create(user=user)
            return redirect("assignments:submissions", slug=self.assignment.slug, 
                    username=self.author.username)
        else:
            context = self.get_context_data()
            context['form'] = form
            return render(self.request, "assignments/submission_list.html", context)

class DownloadSubmission(AssignmentSubmissionVersionMixin, AnalyticsMixin, View):

    def get(self, *args, **kwargs):
        filename = Path(self.submission.upload.file.name).name
        return HttpResponse(self.submission.upload.file.read(), headers={
            'Content-Type': self.submission.mime,
            'Content-Disposition': f'attachment; filename="{filename}"',
        })

class DownloadExample(LoginRequiredMixin, AnalyticsMixin, View):

    def get_object(self):
        return get_object_or_404(AssignmentExample, 
                assignment__slug=self.kwargs['slug'], pk=self.kwargs['pk'])

    def get(self, *args, **kwargs):
        f = self.get_object()
        filename = Path(f.upload.file.name).name
        return HttpResponse(f.upload.file.read(), headers={
            'Content-Type': f.mime,
            'Content-Disposition': f'attachment; filename="{filename}"',
        })







