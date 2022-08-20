from django.core.management.base import BaseCommand, CommandError
from posts.models import Post

class Command(BaseCommand):
    help="Recompile markdown for all PandocMarkdownModel subclasses"

    def handle(self, *args, **kwargs):
        classes = [Post]
        for cls in classes:
            for obj in cls.objects.all():
                obj.compile_markdown()
                obj.save()

