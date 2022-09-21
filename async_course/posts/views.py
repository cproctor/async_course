from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from posts.models import Post
from posts.forms import PostForm, PostReplyForm
from profiles.mixins import AuthorOrTeacherRequiredMixin
from events.models import Event, Notification
from analytics.mixins import AnalyticsMixin
from django.http import HttpResponseRedirect

class PostList(LoginRequiredMixin, AnalyticsMixin, ListView):
    queryset = Post.objects.filter(parent=None).prefetch_related('descendents', 'upvotes', 'publications')
    context_object_name = "posts"

    def get_context_data(self, **kwargs):
        post_notifications = self.request.user.notifications.filter(
                event__action=Event.EventActions.CREATED_POST, read=False).all()
        unseen_post_ids = set([p.event.object_id for p in post_notifications])

        context = super().get_context_data(**kwargs)
        for post in context['posts']:
            tree_ids = set([p.id for p in post.descendents.all()] + [post.id])
            post.is_new = bool(unseen_post_ids.intersection(tree_ids))
        return context

class NewPost(LoginRequiredMixin, AnalyticsMixin, CreateView):
    model = Post
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
            obj.assign_tree_relations()
            obj.update_priority()
            obj.save()
            self.object = obj
            evt = Event(user=obj.author, action=Event.EventActions.CREATED_POST, 
                    object_id=obj.id)
            evt.save()
            for user in obj.interested_people():
                evt.notifications.create(user=user)
            return redirect("posts:detail", pk=obj.id)
        else:
            context = self.get_context_data()
            context["form"] = form
            return render(self.request, self.template_name, context)

class EditPost(AuthorOrTeacherRequiredMixin, AnalyticsMixin, UpdateView):
    model = Post
    template_name = "posts/post_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prompt'] = "Edit post"
        context['url'] = reverse_lazy("posts:edit", args=[self.object.pk])
        return context

    def get_form_class(self):
        if self.get_object().is_root():
            return PostForm
        else:
            return PostReplyForm

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        u = self.request.user
        if not (self.object.editable() or (u.is_authenticated and u.profile.is_teacher)):
            return redirect("posts:detail", pk=self.object.id)
        return super().dispatch(request, *args, **kwargs)

    def post(self, *args, **kwargs):
        obj = self.get_object()
        form = self.get_form_class()(self.request.POST, instance=obj)
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

class ReplyToPost(LoginRequiredMixin, AnalyticsMixin, CreateView):
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
            obj.assign_tree_relations()
            obj.update_priority()
            obj.save()
            return redirect("posts:detail", pk=obj.parent.id)
        else:
            context = self.get_context_data()
            context["form"] = form
            return render(self.request, self.template_name, context)

class UpvotePost(LoginRequiredMixin, AnalyticsMixin, UpdateView):
    model = Post

    def get(self, *args, **kwargs):
        return redirect('posts:detail', pk=self.kwargs['pk'])

    def post(self, *args, **kwargs):
        obj = self.get_object()
        voted = obj.upvotes.filter(voter=self.request.user).exists()
        is_author = obj.author == self.request.user
        if not voted and not is_author:
            obj.upvotes.create(voter=self.request.user)
        return redirect('posts:detail', pk=obj.id)

class ShowPost(LoginRequiredMixin, AnalyticsMixin, DetailView):
    model = Post

    def get(self, *args, **kwargs):
        post = self.get_object()
        if not post.is_root():
            url = reverse_lazy('posts:detail', args=[post.root_post().id]) + f"#post-{post.id}"
            return HttpResponseRedirect(url)
        result = super().get(*args, **kwargs)
        tree_ids = [post.id] + [p.id for p in post.descendents.all()]
        n = self.request.user.notifications.filter(
            event__action=Event.EventActions.CREATED_POST,
            event__object_id__in=tree_ids,
        )
        n.update(read=True)
        return result

