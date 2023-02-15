from django.urls import path, include
from . import views
app_name = "utilit-api"

urlpatterns = [
    path('', views.getstatus, name='get_update'),
]
