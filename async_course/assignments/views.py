from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from common.mixins import AdminRequiredMixin
from .models import Assignment
from .forms import AssignmentForm

class AssignmentList(LoginRequiredMixin, ListView):
    queryset = Assignment.objects.filter(active=True)
    context_object_name = "assignments"

    def get_context_data(self, **kwargs):
        assignments = Assignment.objects.all()
        aws = [[a.get_status(self.request.user), a] for a in assignments]
        context = super().get_context_data(**kwargs)
        context['assignments_with_status'] = aws
        return context

class NewAssignment(AdminRequiredMixin, CreateView):
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
            return redirect("pages:detail", slug=assn.slug)
        else:
            context = self.get_context_data()
            context["form"] = form
            return render(self.request, self.template_name, context)

class EditAssignment(AdminRequiredMixin, UpdateView):
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

