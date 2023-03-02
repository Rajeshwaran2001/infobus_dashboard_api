from django.contrib.auth.views import LoginView

from dashboard import views
from django.urls import path

app_name = "FDashboard"

urlpatterns = [
    path('dash', views.dash, name='dashboard'),
    path('ad_detail/<int:ad_id>', views.view_ad, name='ad_detail'),
    path('', LoginView.as_view(template_name='common/login.html'), name='Flogin'),
    path('route', views.route_summary, name="route_summary"),
    path('route_summary', views.route_summary_filled, name="route_summary_filled"),
    path('update', views.getupdate, name='update'),
    path('Fsignup', views.Franchise_signup_view, name='Fsignup'),
    path('change', views.change_password, name="change"),
    path('today_count', views.update_today_count, name='update_today_count'),
    path('bus_count', views.update_bus_count, name='update_bus_count'),
    path('get_chart_data', views.get_data, name='get_chart_data')
]
