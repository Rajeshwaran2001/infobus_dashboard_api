from django.contrib.auth.views import LoginView
from . import views
from django.urls import path

app_name = "FDashboard"

urlpatterns = [
    path('dashboard', views.dash, name='dashboard'),
    path('ad_detail/<int:ad_id>', views.view_ad, name='ad_detail'),
    path('', LoginView.as_view(template_name='common/login.html'), name='Flogin'),
    path('route', views.route_summary, name="route_summary"),
    path('spot', views.spot, name="spot_ad"),
    path('route_summary', views.route_summary_filled, name="route_summary_filled"),
    path('Fsignup', views.Franchise_signup_view, name='Fsignup'),
    path('change-password', views.change_password, name="change")
]
