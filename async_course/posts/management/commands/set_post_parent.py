from django.core.management.base import BaseCommand, CommandError
from posts.models import Post

class Command(BaseCommand):
    help="Assign a new parent for a post"

    def add_arguments(self, parser):
        parser.add_argument('post', type=int)
        parser.add_argument('parent', type=int)

    def handle(self, *args, **options):
        post = Post.objects.get(pk=options['post'])
        parent = Post.objects.get(pk=options['parent'])
        post.parent = parent
        post.save()
        for p in [post, parent]:
            p.assign_tree_relations()
            p.update_priority()
            p.save()
        
