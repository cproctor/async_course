from pubref.models import PandocMarkdownModel
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
import arrow
import re

class Post(PandocMarkdownModel):
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, related_name="posts", 
            on_delete=models.CASCADE)
    parent = models.ForeignKey("Post", related_name="child_posts", null=True, blank=True,
            on_delete=models.CASCADE)
    ancestors = models.ManyToManyField("Post", related_name="descendents", blank=True)
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
        return (
            1 + 
            self.descendents.count() + 
            self.upvotes.count() + 
            self.publications.count()
        )

    def assign_tree_relations(self):
        "Sets ancestor and descendent relations, based on parent relations"
        self.ancestors.clear()
        parent = self.parent
        while parent:
            self.ancestors.add(parent)
            parent = parent.parent
        descendents = sum([child.tree() for child in self.child_posts.all()], [])
        self.descendents.set(descendents)
        
    def editable(self):
        return self.age_in_hours() < settings.POST_UPVOTE_HOUR_LIMIT

    def is_root(self):
        return self.parent is None

    def root_post(self):
        return self.parent.root_post() if self.parent else self

    def tree(self):
        """Returns a flattened tree of all posts starting from this one
        This method should only be used for (re)constructing trees;
        otherwise self.descendents.all() is more efficient.
        """
        return sum([child.tree() for child in self.child_posts.all()], [self])

    def lede(self):
        text = re.sub('<[^>]+>', '', self.html).split()
        lede_words =  ' '.join(text[:settings.POST_LEDE_WORDS])
        if len(text) > settings.POST_LEDE_WORDS:
            lede_words += '...'
        return lede_words

    def interested_people(self):
        """Returns a list of people who are defined as interested in this object.
        """
        return User.objects.all()

    class Meta:
        ordering = ["-priority",]

class Upvote(models.Model):
    voter = models.ForeignKey(User, related_name="upvotes", 
            on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name="upvotes", 
            on_delete=models.CASCADE)
