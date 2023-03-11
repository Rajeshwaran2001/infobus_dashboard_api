from django.db import models
from django.contrib.auth.models import User
from utility.models import District


# Create your models here.
class Office(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mobile_no_1 = models.CharField(max_length=10, null=True, blank=False)
    is_Active = models.BooleanField(default=True)

    @property
    def get_name(self):
        return self.user.first_name + " " + self.user.last_name

    @property
    def get_instance(self):
        return self

    def __str__(self):
        return self.user.username
