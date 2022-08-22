from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages

class TeacherRequiredMixin(LoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.profile.is_teacher:
            return redirect("common:home")
        return super().dispatch(request, *args, **kwargs)

class AuthorOrTeacherRequiredMixin(LoginRequiredMixin):
    """A view mixin which ensures that the current user is either the object's author or an admin.
    """
    author_attribute_name = "author"

    def get_object_author(self):
        return getattr(self.get_object(), self.author_attribute_name)

    def dispatch(self, request, *args, **kwargs):
        if not (request.user == self.get_object_author() or request.user.profile.is_teacher):
            return redirect("public:home")
        return super().dispatch(request, *args, **kwargs)

