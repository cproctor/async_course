from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from common.email import send_email

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

class TestEmail(TemplateView):
    template_name = "common/email_test.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['index'] = self.kwargs['index']
        return context

    def get(self, *args, **kwargs):
        index = self.kwargs['index']
        send_email(
            f"Email test {index}",
            f"This is a test.",
            [addr for name, addr in settings.ADMINS]
        )
        return super().get(*args, **kwargs)
