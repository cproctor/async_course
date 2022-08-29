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
from assignments.models import Assignment, Submission
from assignments.forms import AssignmentForm, SubmissionForm
from assignments.mixins import AssignmentSubmissionsMixin
import magic
from pathlib import Path

class ListAssignments(LoginRequiredMixin, ListView):
    queryset = Assignment.objects.filter(active=True)
    context_object_name = "assignments"

    def get_context_data(self, **kwargs):
        assignments = Assignment.objects.all()
        aws = [[a.get_status(self.request.user), a] for a in assignments]
        context = super().get_context_data(**kwargs)
        context['assignments_with_status'] = aws
        return context

class NewAssignment(TeacherRequiredMixin, CreateView):
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

class EditAssignment(TeacherRequiredMixin, UpdateView):
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

class ShowAssignment(LoginRequiredMixin, DetailView):
    model = Assignment

class ShowAssignmentRoster(DetailView):
    queryset = Assignment.objects.filter(has_submissions=True)
    template_name = "assignments/assignment_roster.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        students = User.objects.filter(profile__is_student=True).all()
        context['roster'] = [[u, self.object.get_status(u)] for u in students]
        return context

class ShowAssignmentSubmissions(AssignmentSubmissionsMixin, FormMixin, ListView):

    form_class = SubmissionForm

    def dispatch(self, *args, **kwargs):
        destination = super().dispatch(*args, **kwargs)
        self.object_list = self.get_queryset().all()
        return destination

    def get_queryset(self):
        return Submission.objects.filter(assignment=self.assignment, author=self.author)

    def post(self, *args, **kwargs):
        form = self.form_class(self.request.POST, self.request.FILES)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.assignment = self.assignment
            sub.author = self.author
            sub.version = Submission.get_next_version(self.author, self.assignment)
            sub.mime = magic.from_file(sub.upload.file, mime=True)
            sub.save()
            return redirect("assignments:submissions", slug=self.assignment.slug, 
                    username=self.author.username)
        else:
            context = self.get_context_data()
            context['form'] = form
            return render(self.request, "assignments/submission_list.html", context)

class DownloadSubmission(LoginRequiredMixin, View):

    def get_object(self):
        return get_object_or_404(Submission, 
            assignment__slug=self.kwargs['slug'],
            author__username=self.kwargs['username'],
            version=self.kwargs['version']
        )

    def get(self, *args, **kwargs):
        user = self.request.user
        sub = self.get_object()
        if sub.shared or user.profile.is_teacher or user == sub.author:
            filename = Path(sub.upload.file.name).name
            return HttpResponse(sub.upload.file.read(), headers={
                'Content-Type': sub.mime,
                'Content-Disposition': f'attachment; filename="{filename}"',
            })
        else:
            raise PermissionDenied()


