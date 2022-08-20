from pubref.models import PandocMarkdownModel
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
import arrow

class Post(PandocMarkdownModel):
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, related_name="posts", 
            on_delete=models.CASCADE)
    parent = models.ForeignKey("Post", related_name="child_posts", null=True, blank=True,
            on_delete=models.CASCADE)
    title = models.CharField(max_length=200, null=True)
    submissions = models.ManyToManyField("assignments.Submission", related_name="posts")
    priority = models.FloatField(default=1)
    pinned = models.BooleanField(default=False)

    def get_absolute_url(self):
        return f"/posts/{self.id}"

    def update_priority(self):
        self.priority = self.score() / pow(self.age_in_hours() + 2, settings.POST_GRAVITY)

    def age_in_hours(self):
        return (timezone.now() - self.date_created).total_seconds() / (60 * 60)

    def humanized_creation_date(self):
        return arrow.get(self.date_created).humanize()

    def score(self):
        return self.count_tree() + self.upvotes.count() 

    def count_tree(self):
        return 1 + sum(child.count_tree() for child in self.child_posts.all())

    def editable(self):
        return self.age_in_hours() < settings.POST_UPVOTE_HOUR_LIMIT

    class Meta:
        ordering = ["-priority",]

class Upvote(models.Model):
    voter = models.ForeignKey(User, related_name="upvotes", 
            on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name="upvotes", 
            on_delete=models.CASCADE)
