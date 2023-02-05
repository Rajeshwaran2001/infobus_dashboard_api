from django.db import models

# Create your models here.


class MyAds(models.Model):
    imei = models.PositiveIntegerField( null=True, blank=True)
    Count = models.PositiveIntegerField(null=True, blank=True)
    adname = models.CharField(max_length=50, null=True, blank=True)
    date_time = models.CharField(max_length=150, null=True, blank=True)

