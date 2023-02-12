from django.urls import path, include
from rest_framework.authtoken import views

urlpatterns = [

    path('ads/', include('api.ads.urls')),
    path('vehical/', include('api.vehical.urls')),
    path('district/', include('api.District.urls')),
]
