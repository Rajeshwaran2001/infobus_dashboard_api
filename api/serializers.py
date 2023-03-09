from rest_framework import serializers
from utility.models import Ads, District, Slot


class AdSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ads
        fields = ['id', 'AdName', 'AdNameUsername', 'StartDate', 'EndDate', 'TotalCount', 'No_of_Days', 'ECPD', 'ECPM',
                  'BusCount', 'District', 'display']


class DistrictSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'District', 'DistrictTamil', ]


class SlotSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Slot
        fields = ['id', 'Total_spots', 'Filled', 'Empty', 'district']
