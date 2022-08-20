from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView

class HomeView(TemplateView):
    template_name = "common/home.html"

    def dispatch(self, request, *args, **kwargs):
        return redirect("posts:list")
