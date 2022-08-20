from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from .models import Post
from .forms import PostForm, PostReplyForm
from common.mixins import AuthorOrAdminRequiredMixin

class PostList(ListView):
    queryset = Post.objects.filter(parent=None)
    context_object_name = "posts"

class NewPost(LoginRequiredMixin, CreateView):
    form_class = PostForm
    template_name = "posts/post_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prompt'] = "New post"
        context['url'] = reverse_lazy("posts:new")
        return context

    def post(self, *args, **kwargs):
        form = PostForm(self.request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.author = self.request.user
            obj.compile_markdown()
            obj.save()
            obj.update_priority()
            obj.save()
            return redirect("posts:detail", pk=obj.id)
        else:
            context = self.get_context_data()
            context["form"] = form
            return render(self.request, self.template_name, context)

class EditPost(AuthorOrAdminRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "posts/post_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prompt'] = "Edit post"
        context['url'] = reverse_lazy("posts:edit", args=[self.object.pk])
        return context

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj.editable():
            return redirect("posts:detail", pk=obj.id)
        return super().dispatch(request, *args, **kwargs)

    def post(self, *args, **kwargs):
        obj = self.get_object()
        form = PostForm(self.request.POST, instance=obj)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.author = self.request.user
            obj.compile_markdown()
            obj.save()
            return redirect("posts:detail", pk=obj.id)
        else:
            context = self.get_context_data()
            context["form"] = form
            return render(self.request, self.template_name, context)

class ReplyToPost(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostReplyForm
    template_name = "posts/post_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prompt'] = "Reply"
        context['parent'] = self.get_object()
        context['url'] = reverse_lazy("posts:reply", args=[self.kwargs['pk']])
        return context

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        parent = self.get_object()
        form = PostReplyForm(self.request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.author = self.request.user
            obj.parent = parent
            obj.compile_markdown()
            obj.save()
            obj.update_priority()
            obj.save()
            return redirect("posts:detail", pk=obj.parent.id)
        else:
            context = self.get_context_data()
            context["form"] = form
            return render(self.request, self.template_name, context)

class UpvotePost(LoginRequiredMixin, UpdateView):
    model = Post

    def get(self, *args, **kwargs):
        return redirect('posts:detail', pk=self.kwargs['pk'])

    def post(self, *args, **kwargs):
        obj = self.get_object()
        voted = obj.upvotes.filter(voter=self.request.user).exists()
        is_author = obj.author == self.request.user
        if not voted and not is_author:
            obj.upvotes.create(voter=self.request.user)
        return redirect('posts:list')

class ShowPost(DetailView):
    model = Post

