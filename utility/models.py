from django.db import models
import datetime as dt
from django.contrib.auth.models import User


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


class District(models.Model):
    District = models.CharField(max_length=20, null=True, blank=True)
    DistrictTamil = models.CharField(max_length=50, null=True, blank=True)
    is_Active = models.BooleanField(default=True)

    def __str__(self):
        return self.District

    class Meta:
        verbose_name_plural = "District"


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
        return (dt.date.today() - self.StartDate).days


class MyAds(models.Model):
    imei = models.CharField(max_length=50, null=True, blank=True)
    Count = models.PositiveIntegerField(null=True, blank=True)
    adname = models.CharField(max_length=50, null=True, blank=True)
    bus_no = models.CharField(max_length=50, null=True, blank=True)
    route_no = models.CharField(max_length=50, null=True, blank=True)
    route_name = models.CharField(max_length=50, null=True, blank=True)
    date_time = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.adname + ' - ' + self.bus_no

    class Meta:
        verbose_name_plural = "MyAds"


class Slot(models.Model):
    Total_spots = models.PositiveIntegerField(null=True, blank=False)
    Filled = models.PositiveIntegerField(null=True, blank=False)
    Empty = models.PositiveIntegerField(null=True, blank=False)
    district = models.OneToOneField(District, null=True, on_delete=models.CASCADE)
