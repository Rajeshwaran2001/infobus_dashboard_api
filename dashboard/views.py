import requests
from django.db.models import Sum
from django.shortcuts import render, redirect
from api.ads.models import Ads
from dashboard.forms import ServiceUserForm
from django.contrib.auth.models import Group
from .models import MyAds
from django.utils import timezone
import json


# Create your views here.


def listads(request):
    ads = Ads.objects.all()
    for ad in ads:
        ad.myads_count = MyAds.objects.filter(adname=ad.AdName).aggregate(Sum('Count'))['Count__sum']
        if ad.TotalCount:
            ad.percentage = (ad.myads_count / ad.TotalCount) * 100
        else:
            ad.percentage = None
    return render(request, 'Fdashboard/dashboard.html', {'ads': ads})


def service_engineer_signup_view(request):
    userForm = ServiceUserForm()
    mydict = {'userForm': userForm}
    if request.method == 'POST':
        userForm = ServiceUserForm(request.POST)
        if userForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            my_group = Group.objects.get_or_create(name='Franchise')
            my_group[0].user_set.add(user)
        return redirect('FDashboard:Flogin')
    return render(request, 'Fdashboard/signup.html', context=mydict)


def getupdate(request):
    ads = Ads.objects.all()
    for ad in ads:  # Loop ads
        # Prepare the data
        params = {
            'name': ad.AdName,
            'from': ad.StartDate.strftime("%Y-%m-%d"),
            'to': ad.EndDate.strftime("%Y-%m-%d"),
        }
        url = 'https://track.siliconharvest.net/get_adcount.php'  # Request url
        response = requests.get(url, params=params)
        data = response.json()
        print(data)  # For Testing Purpose
        for item in data:
            imei = item.get('imei')
            AdName = ad.AdName
            for key, value in item.items():
                if key == 'imei':
                    continue
                day = key
                count = value
                MyAds.objects.create(adname=AdName, imei=imei, Count=count, date_time=day)
        status_code = response.status_code

        print(len(data))
    return render(request, 'Fdashboard/dashboard.html', {'ads': ads})
