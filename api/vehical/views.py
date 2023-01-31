from django.shortcuts import render
from rest_framework import viewsets
from .models import Vehicle
from .serializers import VehicleSerializer


# Create your views here.
class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all().order_by('id')
    serializer_class = VehicleSerializer
