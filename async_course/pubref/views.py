from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, FormView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from profiles.mixins import AuthorOrTeacherRequiredMixin
from pubref.models import Publication
from pubref.forms import AddPublicationsForm, EditPublicationForm

class PublicationList(LoginRequiredMixin, ListView):
    model = Publication
    context_object_name = "publications"

class AddPublications(LoginRequiredMixin, FormView):
    template_name = "pubref/add_publications_form.html"
    form_class = AddPublicationsForm
    success_url = reverse_lazy("pubref:list")

    def post(self, *args, **kwargs):
        form = AddPublicationsForm(self.request.POST)
        if form.is_valid():
            Publication.import_bibliography(form.cleaned_data["bibtex"], self.request.user)
            Publication.export_bibliography()
            return redirect('pubref:list')
        else:
            context = self.get_context_data()
            context['form'] = form
            return render(self.request, self.template_name, context)

class ShowPublication(LoginRequiredMixin, DetailView):
    model = Publication

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = self.get_object().post_set.all()
        return context

class EditPublication(AuthorOrTeacherRequiredMixin, UpdateView):
    model = Publication
    form_class = EditPublicationForm
    author_attribute_name = "contributor"
    template_name = "pubref/publication_edit.html"

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        pub = get_object_or_404(Publication, slug=self.kwargs["slug"])
        form = EditPublicationForm(self.request.POST, instance=pub)
        if form.is_valid():
            pub.apa_html = pub.get_apa('html')
            pub.apa_text = pub.get_apa('text')
            pub.save()
            Publication.export_bibliography()
            pub.recompile_citing_documents()
            return redirect('pubref:detail', slug=pub.slug)
        else:
            context = self.get_context_data()
            context['form'] = form
            return render(self.request, self.template_name, context)

class DeletePublication(AuthorOrTeacherRequiredMixin, DeleteView):
    model = Publication
    author_attribute_name = "contributor"
    success_url = reverse_lazy('pubref:list')
