from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.contrib.auth.forms import AuthenticationForm

class HomeView(TemplateView):
    template_name = "common/home.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("posts:list")
        else:
            context = {
                'form': AuthenticationForm,
            }
            return render(request, self.template_name, context)
