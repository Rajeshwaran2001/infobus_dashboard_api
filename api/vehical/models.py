from django.db import models
from api.District.models import District
# Create your models here.


class Vehicle(models.Model):
    RouteName = models.ForeignKey(District, on_delete=models.CASCADE)
    VehicleNumer = models.TextField(max_length=6, null=True, blank=False)
