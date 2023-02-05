from django.contrib.auth.views import LoginView

from dashboard import views
from django.urls import path

app_name = "FDashboard"

urlpatterns = [
    path('dash', views.listads, name='dashboard'),
    path('', LoginView.as_view(template_name='Fdashboard/login.html'), name='Flogin'),
    path('update', views.getupdate, name ='update'),
    path('Fsignup', views.service_engineer_signup_view, name='Fsignup'),
]
