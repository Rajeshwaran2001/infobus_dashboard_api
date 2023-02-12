from django.db import models
from django.contrib.auth.models import User
from api.District.models import District
# Create your models here.


class MyAds(models.Model):
    imei = models.CharField(max_length=50, null=True, blank=True)
    Count = models.PositiveIntegerField(null=True, blank=True)
    adname = models.CharField(max_length=50, null=True, blank=True)
    date_time = models.CharField(max_length=150, null=True, blank=True)


class Franchise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='Franchise/', null=True, blank=True)
    address = models.CharField(max_length=50, null=False, blank=False)
    mobile_no_1 = models.CharField(max_length=10, null=False, blank=False)
    mobile_no_2 = models.CharField(max_length=10, null=True, blank=True)
    Date_of_joining = models.DateField(null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    is_Active = models.BooleanField(default=True)

    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name

    @property
    def get_instance(self):
        return self

    def __str__(self):
        return self.user.username
