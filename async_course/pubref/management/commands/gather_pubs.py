from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from posts.models import Post
from zotapi import api
import shutil
from pathlib import Path

class Command(BaseCommand):
    help="Gather Publication files"

    def add_arguments(self, parser):
        parser.add_argument('export', help="Directory in which to export PDFs")
        parser.add_argument('-c', '--clean', action="store_true", help="Clean export dir")

    def handle(self, *args, **options):
        export = self.prepare_export_directory(options)
        for item in api.get_item_ids_and_keys(settings.ZOTERO_COLLECTION):
            citekey = api.get_citation_key(item['id'])
            attachments = api.get_attachments(item['id'])
            for i, att in enumerate(sorted(attachments)):
                filename = citekey + (str(i) if i else '') + att.suffix
                shutil.copy(att, export / filename)

    def prepare_export_directory(self, options):
        export = Path(options['export'])
        if export.exists():
            if not export.is_dir():
                raise IOError(f"{export} exists and is not a directory")
            if any(export.iterdir()):
                if options['clean']:
                    shutil.rmtree(export)
                    export.mkdir()
                else:
                    raise IOError(f"{export} is not empty")
        else:
            export.mkdir(parents=True)
        return export
