from django.contrib.auth.views import LoginView

from dashboard import views
from django.urls import path

app_name = "FDashboard"

urlpatterns = [
    path('dash', views.dash, name='dashboard'),
    path('ad_detail/<int:ad_id>', views.view_ad, name='ad_detail'),
    path('', LoginView.as_view(template_name='common/login.html'), name='Flogin'),
    path('update', views.getupdate, name='update'),
    path('Fsignup', views.Franchise_signup_view, name='Fsignup'),
    path('d', views.api_view, name='update')
]
