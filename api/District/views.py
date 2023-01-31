from django.shortcuts import render
from rest_framework import viewsets
from .models import District
from .serializers import DistrictSerializer


# Create your views here.
class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all().order_by('id')
    serializer_class = DistrictSerializer
