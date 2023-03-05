from django.db import models
import datetime as dt
from api.District.models import District


# Create your models here.
class Ads(models.Model):
    AdName = models.CharField(max_length=30, null=False, blank=False)
    AdNameTamil = models.CharField(max_length=30, null=True, blank=True)
    StartDate = models.DateField()
    EndDate = models.DateField()
    TotalCount = models.IntegerField(null=True, blank=True)
    No_of_Days = models.IntegerField(null=False, blank=False)
    ECPD = models.IntegerField(null=True, blank=False)
    ECPM = models.IntegerField(null=True, blank=False)
    BusCount = models.IntegerField(null=True, blank=True)
    District = models.ManyToManyField(District, blank=True)
    display = models.BooleanField(default=True, help_text="check this to display the ads")

    class Meta:
        verbose_name_plural = "Ads"

    @property
    def current(self):
        return (self.EndDate - self.StartDate).days

    @property
    def diff(self):
        return (self.EndDate - dt.date.today()).days

    @property
    def day(self):
        return (dt.date.today()-self.StartDate).days
