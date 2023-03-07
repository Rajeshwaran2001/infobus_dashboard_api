from django.db import models
import datetime as dt
from api.District.models import District
from django.contrib.auth.models import User


# Create your models here.
class Ads(models.Model):
    AdName = models.CharField(max_length=30, null=False, blank=False)
    AdNameUsername = models.CharField(max_length=30, null=True, blank=False, unique=True)
    StartDate = models.DateField()
    EndDate = models.DateField()
    TotalCount = models.IntegerField(null=True, blank=False)
    No_of_Days = models.IntegerField(null=False, blank=False)
    ECPD = models.IntegerField(null=True, blank=False)
    ECPM = models.IntegerField(null=True, blank=False)
    BusCount = models.IntegerField(null=True, blank=False)
    District = models.ManyToManyField(District, blank=False)
    display = models.BooleanField(default=True, help_text="check this to display the ads")
    agent = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.AdName

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
