from django.db import models


# Create your models here.


class District(models.Model):
    District = models.CharField(max_length=20, null=True, blank=True)
    DistrictTamil = models.CharField(max_length=50, null=True, blank=True)
    is_Active = models.BooleanField(default=True)

    def __str__(self):
        return self.District
    class Meta:
        verbose_name_plural = "District"
