from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('ads', views.AdViewSet)
router.register('district', views.DistrictViewSet)

urlpatterns = [
    path('', include(router.urls))
]
