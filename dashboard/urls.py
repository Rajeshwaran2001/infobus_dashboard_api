from dashboard import views
from django.urls import path

app_name = "FDashboard"

urlpatterns = [
    path('', views.listads, name='dashboard'),
]
