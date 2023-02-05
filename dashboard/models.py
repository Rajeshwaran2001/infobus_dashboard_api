from django.db import models

# Create your models here.


class MyAds(models.Model):
    imei = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=20, null=True, blank=True)
    bus_no = models.CharField(max_length=15, null=True, blank=True)
    adname = models.CharField(max_length=50, null=True, blank=True)
    date_time = models.CharField(max_length=150, null=True, blank=True)

