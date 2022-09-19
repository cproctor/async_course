from django.core.management.base import BaseCommand, CommandError
from posts.models import Post

class Command(BaseCommand):
    help="Assign root post for all posts"

    def handle(self, *args, **kwargs):
        for root_post in Post.objects.filter(parent=None).all():
            for descendent in root_post.tree():
                if descendent != root_post:
                    descendent.root = root_post
                    descendent.save()
