from django.contrib.auth.views import LoginView
from . import views
from django.urls import path

app_name = "Office"

urlpatterns = [
    path('', LoginView.as_view(template_name='common/login.html'), name='Office-login'),
    path('office-signup', views.Office_signup_view, name='office-signup'),
    path('dashboard', views.dashboard, name='office-dashboard'),
    path('ad_detail/<int:ad_id>', views.view_ad, name="ad_detail"),
    path('change-password', views.change_password, name="change"),
]
