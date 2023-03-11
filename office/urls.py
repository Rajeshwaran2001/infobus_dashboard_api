from django.contrib.auth.views import LoginView
from . import views
from django.urls import path

app_name = "Office"

urlpatterns = [
    path('', LoginView.as_view(template_name='common/login.html'), name='Office-login'),
    path('office-signup', views.Office_signup_view, name='office-signup'),
    path('office-dashboard', views.dashboard, name='office-dashboard'),
]
