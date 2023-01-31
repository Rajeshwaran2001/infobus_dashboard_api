from django.shortcuts import render
from api.ads.models import Ads

# Create your views here.

def listads(request):
    ads = Ads.objects.all()

    return render(request, 'Fdashboard/dashboard.html', {'ads': ads})
