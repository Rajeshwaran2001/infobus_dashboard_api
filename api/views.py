from rest_framework import viewsets
from api.serializers import AdSerializer, DistrictSerializer, SlotSerializer
from utility.models import Ads, District, Slot


# Create your views here.
class AdViewSet(viewsets.ModelViewSet):
    queryset = Ads.objects.all().order_by('id')
    serializer_class = AdSerializer


class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all().order_by('id')
    serializer_class = DistrictSerializer


class SlotViewSet(viewsets.ModelViewSet):
    queryset = Slot.objects.all().order_by('id')
    serializer_class = SlotSerializer
