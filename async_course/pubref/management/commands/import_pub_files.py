from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.conf import settings
import shutil
from pathlib import Path
from pubref.models import Publication, PublicationFile
import magic

class Command(BaseCommand):
    help="Import publication files from a directory"

    def add_arguments(self, parser):
        parser.add_argument('import_dir', help="Source directory for PDFs")
        parser.add_argument('-c', '--clean', action="store_true", 
                help="Clean existing pub files")

    def handle(self, *args, **options):
        """Assumes filenames are like:
         - proctor2022.pdf
         - proctor2022_part4.pdf
        """
        if options['clean']:
            for pf in PublicationFile.objects.all():
                pf.delete()
        for f in Path(options['import_dir']).iterdir():
            filename_tokens = f.stem.split('_part')
            citekey = filename_tokens[0]
            print(f, citekey)
            i = int(filename_tokens[1]) if len(filename_tokens) > 1 else None
            try:
                pub = Publication.objects.get(slug=citekey)
                mime = magic.from_file(f, mime=True)
                with f.open('rb') as fh:
                    pub.files.create(
                        upload=File(fh, name=f.name),
                        mime=mime,
                        description=f"part {i}" if i else None
                    )
            except Publication.DoesNotExist:
                print(f" - No publication with citekey {citekey}")
