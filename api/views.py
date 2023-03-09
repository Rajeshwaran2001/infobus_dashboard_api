from rest_framework import viewsets
from api.serializers import AdSerializer, DistrictSerializer
from utility.models import Ads, District


# Create your views here.
class AdViewSet(viewsets.ModelViewSet):
    queryset = Ads.objects.all().order_by('id')
    serializer_class = AdSerializer

class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all().order_by('id')
    serializer_class = DistrictSerializer
