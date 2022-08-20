from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages

class AdminRequiredMixin(LoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect("public:home")
        return super().dispatch(request, *args, **kwargs)

class AuthorOrAdminRequiredMixin(LoginRequiredMixin):
    """A view mixin which ensures that the current user is either the object's author or an admin.
    """
    author_attribute_name = "author"

    def dispatch(self, request, *args, **kwargs):
        author = getattr(self.get_object(), self.author_attribute_name)
        if not (request.user == author or request.user.is_superuser):
            return redirect("public:home")
        return super().dispatch(request, *args, **kwargs)

