from rest_framework import serializers
from .models import Ads


class AdSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ads
        fields = ['AdName', 'StartDate', 'EndDate', 'TotalCount', 'No_of_Days', 'EDC', 'EMC']
