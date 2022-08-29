from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.conf import settings
import shutil
from pathlib import Path
from assignments.models import Assignment, AssignmentExample
import magic

class Command(BaseCommand):
    help="Import assignment examples from import_dir/assn_slug/f"

    def add_arguments(self, parser):
        parser.add_argument('import_dir', help="Source directory for examples")
        parser.add_argument('-c', '--clean', action="store_true", 
                help="Clean existing examples")

    def handle(self, *args, **options):
        if options['clean']:
            for ae in AssignmentExample.objects.all():
                ae.delete()
        for d in Path(options['import_dir']).iterdir():
            try:
                assn = Assignment.objects.get(slug=d.name)
                for f in d.iterdir():
                    mime = magic.from_file(f, mime=True)
                    with f.open('rb') as fh:
                        assn.examples.create(
                            upload=File(fh, name=f.name),
                            description=f.name,
                            mime=mime
                        )
            except Assignment.DoesNotExist:
                print(f" - No assignment with slug {d.name}")
