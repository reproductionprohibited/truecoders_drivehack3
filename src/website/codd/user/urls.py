from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .forms import UserLoginForm

app_name = 'user'
urlpatterns = [
    path(
        'login/',
        LoginView.as_view(
            template_name='user/login.html',
            form_class=UserLoginForm,
        ),
        name='login'
    ),
    path(
        'logout/',
        LogoutView.as_view(
            template_name='user/logout.html'
        ),
        name='logout'
    )
]
