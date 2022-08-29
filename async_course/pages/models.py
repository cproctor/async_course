from pubref.models import PandocMarkdownModel
from django.db import models

class Page(PandocMarkdownModel):
    slug = models.CharField(max_length=40, unique=True)
    in_menu = models.BooleanField(default=False)
    menu_label = models.CharField(max_length=40)
    weight = models.IntegerField(default=0)

    def get_absolute_url(self):
        return f"/pages/{self.slug}"

    class Meta:
        ordering = ["-weight"]
