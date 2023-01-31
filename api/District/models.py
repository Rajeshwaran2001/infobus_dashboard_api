from django.db import models

# Create your models here.


class District(models.Model):
    District = models.CharField(max_length=20, null=True, blank=True)
    DistrictTamil = models.CharField(max_length=50, null=True, blank=True)
