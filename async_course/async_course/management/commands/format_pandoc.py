from django.core.management.base import BaseCommand, CommandError
from pandoc import pandoc

class Command(BaseCommand):
    help="Format text via pandoc"
    
    def add_arguments(self, parser):
        parser.add_argument("markdown")

    def handle(self, *args, **options):
        result = pandoc(options["markdown"])
        self.stdout.write(result)
