from django.urls import path, include
from . import views
app_name = "utilit-api"

urlpatterns = [
    path('bus-detail-update', views.getstatus, name='get_update'),
    path('ad-update', views.getupdate, name='update'),

    # Ajax call
    path('today_count', views.update_today_count, name='update_today_count'),
    path('bus_count', views.update_bus_count, name='update_bus_count'),
    path('get_chart_data', views.get_data, name='get_chart_data')
]
