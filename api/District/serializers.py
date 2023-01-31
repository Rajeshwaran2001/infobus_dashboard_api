from rest_framework import serializers
from .models import District


class DistrictSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'District', 'DistrictTamil', ]
