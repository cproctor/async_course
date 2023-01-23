import re
from model_utils.managers import InheritanceManager
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from .pandoc import (
    markdown_to_html, 
    replace_reference_link,
    PandocConversionError,
)
from .formatting import format_bibtex
from pybtex.database import parse_string
from pybtex.exceptions import PybtexError

def validate_slug(value):
    if not re.match('^[-\w]+$', value):
        raise ValidationError(f"'{value}' is not a valid citation key. Only numbers, letters, hyphens, and underscores are allowed.")

class Publication(models.Model):
    slug = models.CharField(max_length=40, db_index=True, unique=True, validators=[validate_slug])
    bibtex = models.TextField()
    apa_html = models.TextField()
    apa_text = models.TextField()
    contributor = models.ForeignKey(User, related_name="publications", 
            on_delete=models.CASCADE, null=True)

    slug_pattern = "@[0-9a-z_\-]+"

    def __str__(self):
        return self.slug

    @classmethod
    def export_bibliography(cls):
        with open(settings.BIBLIOGRAHY, 'w') as fh:
            fh.write('\n'.join([pub.validated_bibtex() for pub in Publication.objects.all()]))

    @classmethod
    def import_bibliography(cls, bib_string, contributor):
        """Reads in a bibliography and returns results.
        """
        try:
            bib = parse_string(bib_string, 'bibtex')
        except Exception as e:
            return [{
                "pub": None,
                "result": "error",
                "message": e
                }]

        results = []
        for slug, entry in bib.entries.items():
            try:
                pub = Publication.objects.get(slug=slug)
                results.append({
                    "pub": pub, 
                    "result": "exists", 
                    "message": f"{pub.slug} is already in the library"
                })
            except Publication.DoesNotExist:
                pub = Publication(slug=slug, bibtex=entry.to_string('bibtex'), 
                        contributor=contributor)
                try:
                    pub.apa_html = pub.get_apa()
                    pub.apa_text = pub.get_apa('text')
                    pub.full_clean()
                    pub.save()
                    results.append({"pub": pub, "result": "created", "message": "OK"})
                except ValidationError as e:
                    if 'slug' in e.message_dict:
                        results.append({
                            "pub": None, 
                            "result": "error", 
                            "message": ''.join(e.message_dict['slug'])
                        })
                    else:
                        results.append({
                            "pub": None, 
                            "result": "error", 
                            "message": e
                        })
                except PybtexError as e:
                    results.append({
                        "pub": pub, 
                        "result": "error", 
                        "message": e
                    })
        return results

    class InvalidBibtex(Exception):
        pass

    def validated_bibtex(self):
        """Returns a bibtex string which has passed through pybtex
        """
        return parse_string(self.bibtex, 'bibtex').to_string('bibtex')

    def get_slug_from_bibtex(self):
        """Extract the publication key from the bibtex
        """
        bib = parse_string(self.bibtex, 'bibtex')
        bibentries = list(bib.entries.items())
        if len(bibentries) != 1:
            raise Publication.InvalidBibtex("The bibtex must contain a single entry.")
        slug, entry = bibentries[0]
        return slug

    def recompile_citing_documents(self):
        """Recompile markdown for all citing documents. 
        Should be used after the publication changes. 
        """
        relations = [
            'assignment_set', 
            'page_set', 
            'post_set', 
            'profile_set', 
            'review_set', 
        ]
        for relation in relations:
            for doc in getattr(self, relation).all():
                doc.compile_markdown()
                doc.save()
                print(doc)

    def get_apa(self, output='html'):
        """Generates HTML for the entry in APA format.
        """
        return format_bibtex(self.bibtex, output=output)

    def get_absolute_url(self):
        return str(reverse_lazy('pubref:detail', args=[self.slug]))

    class Meta:
        ordering = ['apa_text']

class PandocMarkdownModel(models.Model):
    """An abstract model whose markdown text can be compiled to HTML using Pandoc.
    Extracts references and creates relations.
    """
    markdown = models.TextField(default="")
    html = models.TextField(default="")
    valid = models.BooleanField(default=False)
    error = models.TextField(null=True)
    publications = models.ManyToManyField(Publication)

    objects = InheritanceManager()

    def compile_markdown(self):
        """Processes the model's markdown.
        When successful, the result is stored in the instance's `html`. Otherwise, 
        pandoc's error message is stored in `error` and `valid` is set to False.
        """
        try:
            markdown = self.markdown
            if self.has_citations():
                markdown += "\n\n## References\n"
            html = markdown_to_html(markdown)
            self.html = html
            self.valid = True
            self.error = None
            if self.id is None:
                self.save()
            return self.update_publications()
        except PandocConversionError as e:
            self.valid = False
            self.error = str(e)

    def has_citations(self):
        return len(self.get_citation_slugs()) > 0

    def get_citation_slugs(self):
        slugs = re.findall(Publication.slug_pattern, self.markdown)
        return [slug[1:] for slug in slugs]

    def update_publications(self):
        """Extracts pandoc (citeproc) references and populates `publications`.
        Returns reference slugs which lack publcations.
        """
        publications = []
        slugs_without_publications = []
        for slug in self.get_citation_slugs():
            try:
                pub = Publication.objects.get(slug=slug)
                publications.append(pub)
                self.html = replace_reference_link(self.html, pub)
            except Publication.DoesNotExist:
                print(f"Didn't find {slug}")
                slugs_without_publications.append(slug)
        self.publications.set(publications)
        return slugs_without_publications

    class Meta:
        abstract = True

class PublicationFile(models.Model):
    description = models.TextField(null=True, blank=True)
    publication = models.ForeignKey(Publication, related_name="files", 
            on_delete=models.CASCADE)
    upload = models.FileField(upload_to="publications/")
    mime = models.CharField(max_length=100, default="application/pdf")

    class Meta:
        ordering = ['description']

