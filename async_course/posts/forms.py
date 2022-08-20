from django.forms import ModelForm
from .models import Post, Upvote

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'markdown']

class PostReplyForm(ModelForm):
    class Meta:
        model = Post
        fields = ['markdown']
