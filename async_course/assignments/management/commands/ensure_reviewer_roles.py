from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from assignments.models import Assignment
from reviews.models import ReviewerRole

class Command(BaseCommand):
    help="Set each teacher as reviewer for each student and assignment, and self-reviewers"

    def handle(self, *args, **kwargs):
        for teacher in User.objects.filter(profile__is_teacher=True).all():
            for assignment in Assignment.objects.all():
                for student in User.objects.filter(profile__is_student=True).all():
                    role, created = ReviewerRole.objects.get_or_create(
                        reviewer=teacher,
                        reviewed=student,
                        assignment=assignment,
                    )
                    role.authoritative = True
                    role.status = role.get_status()
                    role.save()
                    ReviewerRole.objects.get_or_create(
                        reviewer=student,
                        reviewed=student,
                        assignment=assignment,
                    )
                    role.authoritative = False
                    role.status = role.get_status()
                    role.save()
                    if assignment.peer_review and student.groups.exists():
                        group = student.groups.first()
                        for peer in group.user_set.exclude(username=student.username).all():
                            ReviewerRole.objects.get_or_create(
                                reviewer=peer,
                                reviewed=student,
                                assignment=assignment,
                            )
                            role.authoritative = False
                            role.status = role.get_status()
                            role.save()



