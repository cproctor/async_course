from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.shortcuts import render, redirect
from django.http import Http404
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404
from .models import Profile
from .forms import ProfileForm
from posts.models import Post
from profiles.mixins import AuthorOrTeacherRequiredMixin
from lai_619.grades import LAI619Grader

class ShowProfile(DetailView):
    model = Profile

    def get_object(self, queryset=None):
        try:
            return Profile.objects.get(user__username=self.kwargs["username"])
        except Profile.DoesNotExist:
            raise Http404("User not found")

    def get_user(self):
        return self.get_object().user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.filter(author=self.get_user()).all()
        return context

class ShowGrades(DetailView):
    model = Profile
    template_name = "profiles/profile_grades.html"

    def get_object(self, queryset=None):
        try:
            return Profile.objects.get(user__username=self.kwargs["username"])
        except Profile.DoesNotExist:
            raise Http404("User not found")

    def get_context_data(self, **kwargs):
        grader = LAI619Grader()
        context = super().get_context_data(**kwargs)
        context['grades'] = grader.get_grades(self.request.user)
        return context

class EditProfile(AuthorOrTeacherRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "profiles/profile_form.html"
    author_attribute_name = "user"
    pk_url_kwarg = "username"

    def get_object(self):
        return get_object_or_404(Profile, user__username=self.kwargs['username'])
        
    def get(self, *args, **kwargs):
        profile = self.get_object()
        form = ProfileForm({
            'first_name': profile.user.first_name,
            'last_name': profile.user.last_name,
            'username': profile.user.username,
            'markdown': profile.markdown,
        }, profile.user)
        print(form)
        context = {
            'profile': profile,
            'form': form,
            'url': reverse_lazy('profiles:edit', args=[profile.user.username])
        }
        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        profile = self.get_object()
        form = ProfileForm(self.request.POST, profile.user)
        if form.is_valid(): 
            profile.markdown = form.cleaned_data['markdown']
            profile.compile_markdown()
            profile.save()
            profile.user.first_name = form.cleaned_data['first_name']
            profile.user.last_name = form.cleaned_data['last_name']
            profile.user.username = form.cleaned_data['username']
            profile.user.save()
            return redirect('profiles:detail', username=profile.user.username)
        else:
            context = {
                'profile': profile,
                'form': form,
                'url': reverse_lazy('profiles:edit', self.request.user.username)
            }
            return render(self.request, self.template_name, context)
