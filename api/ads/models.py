from django.db import models


# Create your models here.
class Ads(models.Model):
    AdName = models.CharField(max_length=30, null=False, blank=False)
    AdNameTamil = models.CharField(max_length=30, null=True, blank=False)
    StartDate = models.DateField()
    EndDate = models.DateField()
    TotalCount = models.IntegerField(null=True, blank=True)
    No_of_Days = models.IntegerField(null=False, blank=False)
    ECPD = models.IntegerField(null=True, blank=False)
    ECPM = models.IntegerField(null=True, blank=False)
    BusCount = models.IntegerField(null=True, blank=True)
    District = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Ads"

