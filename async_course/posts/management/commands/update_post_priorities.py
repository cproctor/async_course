from django.core.management.base import BaseCommand, CommandError
from posts.models import Post

class Command(BaseCommand):
    help="Update priority of all posts"

    def handle(self, *args, **kwargs):
        for post in Post.objects.all():
            post.update_priority()
            post.save()
