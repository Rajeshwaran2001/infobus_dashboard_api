from rest_framework import serializers
from .models import Ads


class AdSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ads
        fields = ['id', 'AdName', 'AdNameUsername', 'StartDate', 'EndDate', 'TotalCount', 'No_of_Days', 'ECPD', 'ECPM',
                  'BusCount', 'District', 'display']
