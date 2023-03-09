from rest_framework import serializers
from utility.models import Ads, District


class AdSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ads
        fields = ['id', 'AdName', 'AdNameUsername', 'StartDate', 'EndDate', 'TotalCount', 'No_of_Days', 'ECPD', 'ECPM',
                  'BusCount', 'District', 'display']


class DistrictSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'District', 'DistrictTamil', ]
