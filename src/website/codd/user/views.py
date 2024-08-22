from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView

from .forms import UserLoginForm


class CustomLoginView(LoginView):
    template_name = 'login.html',
    redirect_authenticated_user = True
    success_url = reverse_lazy('zipprocessor:homepage')
    form_class = UserLoginForm