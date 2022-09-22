from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from events.models import Event
from assignments.models import Submission
from reviews.models import Review
from posts.models import Post

class DoesNotExist(Exception):
    pass

class Command(BaseCommand):
    help="Recreate notifications based on updated interested_people"

    def handle(self, *args, **kwargs):
        for user in User.objects.all():
            for event in Event.objects.all():
                try:
                    obj = self.get_object(event)
                    read = event.notifications.filter(user=user, read=True).exists()
                    event.notifications.filter(user=user).delete()
                    if user in obj.interested_people():
                        event.notifications.create(user=user, read=read)
                except DoesNotExist:
                    event.delete()

    def get_object(self, event):
        if event.action == Event.EventActions.CREATED_POST:
            Model = Post
        elif event.action == Event.EventActions.ADDED_SUBMISSION:
            Model = Submission
        elif event.action == Event.EventActions.ADDED_REVIEW:
            Model = Review
        else:
            raise DoesNotExist()
        try:
            return Model.objects.get(pk=event.object_id)
        except (Post.DoesNotExist, Submission.DoesNotExist, Review.DoesNotExist):
            raise DoesNotExist()

        

