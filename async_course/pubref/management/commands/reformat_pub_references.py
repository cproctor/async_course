from django.core.management.base import BaseCommand, CommandError
from pubref.models import Publication

class Command(BaseCommand):
    help="Regenerate APA styling of references"

    def handle(self, *args, **kwargs):
        for pub in Publication.objects.all():
            pub.apa_html = pub.get_apa('html')
            pub.apa_text = pub.get_apa('text')
            pub.save()
