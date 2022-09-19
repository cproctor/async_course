from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from reviews.models import ReviewerRole

class Command(BaseCommand):
    help="Update all review_roles with correct status"

    def handle(self, *args, **kwargs):
        for rr in ReviewerRole.objects.all():
            rr.status = rr.get_status()
            rr.save()
