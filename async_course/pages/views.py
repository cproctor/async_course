from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from profiles.mixins import TeacherRequiredMixin
from pages.models import Page
from pages.forms import PageForm

class PageList(TeacherRequiredMixin, ListView):
    model = Page
    context_object_name = "pages"

class NewPage(TeacherRequiredMixin, CreateView):
    model = Page
    form_class = PageForm
    template_name = "pages/page_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prompt'] = "New page"
        context['url'] = reverse_lazy("pages:new")
        return context

    def post(self, *args, **kwargs):
        form = PageForm(self.request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            page.compile_markdown()
            page.save()
            return redirect("pages:detail", slug=page.slug)
        else:
            context = self.get_context_data()
            context["form"] = form
            return render(self.request, self.template_name, context)
    
class EditPage(TeacherRequiredMixin, UpdateView):
    model = Page
    form_class = PageForm
    template_name = "pages/page_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prompt'] = "Edit page"
        context['url'] = reverse_lazy("pages:edit", args=[self.get_object().slug])
        return context

    def post(self, *args, **kwargs):
        form = PageForm(self.request.POST, instance=self.get_object())
        if form.is_valid():
            page = form.save(commit=False)
            page.compile_markdown()
            page.save()
            return redirect("pages:detail", slug=page.slug)
        else:
            context = self.get_context_data()
            context["form"] = form
            return render(self.request, self.template_name, context)

class ShowPage(LoginRequiredMixin, DetailView):
    model = Page
