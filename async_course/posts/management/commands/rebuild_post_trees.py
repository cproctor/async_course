from django.core.management.base import BaseCommand, CommandError
from posts.models import Post

class Command(BaseCommand):
    help="Reset the ancestor/descendent relations for all posts, based on parent."

    def handle(self, *args, **kwargs):
        for post in Post.objects.all():
            post.ancestors.clear()
        for post in Post.objects.all():
            parent = post.parent
            while parent:
                post.ancestors.add(parent)
                parent = parent.parent
                

        

