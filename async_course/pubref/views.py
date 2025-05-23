from pathlib import Path
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, FormView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, Http404
from django.conf import settings
from profiles.mixins import AuthorOrTeacherRequiredMixin
from pubref.models import Publication, PublicationFile
from pubref.forms import AddPublicationsForm, EditPublicationForm
from analytics.mixins import AnalyticsMixin

class PublicationList(LoginRequiredMixin, AnalyticsMixin, ListView):
    model = Publication
    context_object_name = "publications"

class AddPublications(LoginRequiredMixin, AnalyticsMixin, FormView):
    template_name = "pubref/add_publications_form.html"
    form_class = AddPublicationsForm
    success_url = reverse_lazy("pubref:list")

    def post(self, *args, **kwargs):
        form = AddPublicationsForm(self.request.POST)
        if form.is_valid():
            result = Publication.import_bibliography(
                    form.cleaned_data["bibtex"], self.request.user)
            self.report_import_results(result)
            Publication.export_bibliography()
            return redirect('pubref:list')
        else:
            context = self.get_context_data()
            context['form'] = form
            return render(self.request, self.template_name, context)

    def report_import_results(self, results):
        d = duplicates = [r for r in results if r['result'] == 'exists']
        e = errors = [r for r in results if r['result'] == 'error']
        s = successes = [r for r in results if r['result'] == 'created']

        def pluralizer(singular, plural):
            def pl(iterable):
                return singular if len(iterable) == 1 else plural
            return pl

        was = pluralizer("was", "were")
        pub = pluralizer("publication", "publications")

        if not successes and not duplicates and not errors:
            msg = "No publications were found."
        elif not duplicates and not errors:
            if len(results) == 1:
                msg = f"{results[0]['pub'].slug} was imported."
            else:
                msg = f"All {len(s)} publications were imported."
        else:
            if successes:
                msg = f"{len(s)} {pub(s)} {was(s)} added."
            else:
                msg = "No publications were added."
            if duplicates:
                msg += f" {len(d)} {was(d)} already in the bibliography."
            if errors:
                msg += " The following import errors occured:<ul>"
                for err in errors:
                    msg += f"<li>{err['message']}</li>"
                msg += "</ul>"
        if successes and not errors:
            messages.info(self.request, msg)
        else:
            messages.warning(self.request, msg)

class ShowPublication(LoginRequiredMixin, AnalyticsMixin, DetailView):
    model = Publication

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = self.get_object().post_set.all()
        return context

class PublicationListBibtex(LoginRequiredMixin, AnalyticsMixin, View):

    def get(self, *args, **kwargs):
        bibfile = Path(settings.BIBLIOGRAHY)
        if bibfile.exists():
            return HttpResponse(bibfile.read_text(), headers={
                'Content-Type': "application/x-bibtex",
                'Content-Disposition': f'attachment; filename="lai_619.bib"',
            })
        else:
            raise Http404("No publications have been added yet")

class EditPublication(AuthorOrTeacherRequiredMixin, AnalyticsMixin, UpdateView):
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
            pub.slug = pub.get_slug_from_bibtex()
            pub.save()
            Publication.export_bibliography()
            pub.recompile_citing_documents()
            return redirect('pubref:detail', slug=pub.slug)
        else:
            context = self.get_context_data()
            context['form'] = form
            return render(self.request, self.template_name, context)

class DeletePublication(AuthorOrTeacherRequiredMixin, AnalyticsMixin, DeleteView):
    model = Publication
    author_attribute_name = "contributor"
    success_url = reverse_lazy('pubref:list')

class DownloadPublicationFile(LoginRequiredMixin, AnalyticsMixin, View):
    def get_object(self):
        return get_object_or_404(PublicationFile, 
                publication__slug=self.kwargs['slug'], pk=self.kwargs['pk'])

    def get(self, *args, **kwargs):
        f = self.get_object()
        filename = Path(f.upload.file.name).name
        return HttpResponse(f.upload.file.read(), headers={
            'Content-Type': f.mime,
            'Content-Disposition': f'attachment; filename="{filename}"',
        })





