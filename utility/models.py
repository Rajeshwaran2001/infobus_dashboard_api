from django.db import models


# Create your models here.
class bus_Detail(models.Model):
    bus_no = models.CharField(max_length=10)
    city = models.CharField(max_length=20)
    depo = models.CharField(max_length=20)
    route_no = models.CharField(max_length=10)
    route_name = models.CharField(max_length=50)
    imei = models.CharField(max_length=20)
    station = models.CharField(max_length=20)
    position = models.CharField(max_length=50)
