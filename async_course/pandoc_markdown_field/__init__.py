from django.db import models
from django import forms
import subprocess
from django.conf import settings
from .temp_file import TempFile

class PandocMarkdownField(models.JSONField):
    """A model field representing a pandoc-flavored Markdown document and its rendering.

    A note on validation: Invalid markdown is still valid input: When a user submits invalid markdown, 
    we want to save this so that they can still see and edit their erroneous input. 
    """
    description = "A field containing pandoc-flavored markdown source, rendered HTML, and error messages."

    def to_python(self, value):
        """Converts a value into a dict suitable for JSON serialization.
        When `value` is a string, it's presumed to be raw markdown. 
        When `value` is a dict, it's presumed to have already been processed.
        When `value` is None, we use the empty string.
        """
        if isinstance(value, str):
            markdown = value
        elif isinstance(value, dict) and "markdown" in value.keys():
            markdown = value["markdown"]
        elif value == None:
            markdown = None
        else:
            raise ValueError(f"Unexpected value: {value}")
        return self.parse_markdown(markdown)

    def pre_save(self, instance, add):
        markdown = getattr(instance, self.attname)["markdown"]
        parsed = self.parse_markdown(

    def parse_markdown(self, markdown):
        """Tries to marse `markdown` to HTML, returning a dict.
        """
        if markdown.strip() == '':
            return {
                "markdown": "", 
                "html":"", 
                "error": None
            }

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.TextInput}
        defaults.update(kwargs)
        return super().formfield(**defaults)
