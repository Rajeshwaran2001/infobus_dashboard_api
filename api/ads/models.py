from django.db import models


# Create your models here.
class Ads(models.Model):
    AdName = models.CharField(max_length=30, null=False, blank=False)
    StartDate = models.DateField()
    EndDate = models.DateField()
    TotalCount = models.IntegerField(null=True, blank=True)
    No_of_Days = models.IntegerField(null=False, blank=False)
    EDC = models.IntegerField(null=True, blank=False)
    EMC = models.IntegerField(null=True, blank=False)

    class Meta:
        verbose_name_plural = "Ads"
