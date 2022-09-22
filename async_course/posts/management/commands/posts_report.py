from statistics import mean, median, stdev
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from posts.models import Post

class Command(BaseCommand):
    help="Reset the ancestor/descendent relations for all posts, based on parent."

    def handle(self, *args, **kwargs):
        counts, points = [], []
        for user in User.objects.filter(profile__is_teacher=False).all():
            counts.append(user.posts.count())
            points.append(sum([p.score() for p in user.posts.all()]))
        print(f"Post count: mean {round(mean(counts), 1)}, median {round(median(counts), 1)}, stdev {round(stdev(counts), 1)}")
        print(f"Total points: mean {round(mean(points), 1)}, median {round(median(points), 1)}, stdev {round(stdev(points), 1)}")
                

        

