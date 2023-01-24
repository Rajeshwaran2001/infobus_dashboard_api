from rest_framework import viewsets
from django.shortcuts import render
from .serializers import AdSerializer
from .models import Ads

# Create your views here.
class AdViewSet(viewsets.ModelViewSet):
    queryset = Ads.objects.all().order_by('id')
    serializer_class = AdSerializer
