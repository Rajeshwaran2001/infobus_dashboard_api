import requests
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect
from api.ads.models import Ads
from dashboard.forms import ServiceUserForm
from django.contrib.auth.models import Group
from .models import MyAds
from json.decoder import JSONDecodeError
import logging

logger = logging.getLogger(__name__)


# Create your views here.


def listads(request):
    ads = Ads.objects.all()
    ten_days = []
    five_days = []
    for ad in ads:
        if ad.current <= 10 and ad.current >= 5:
            ten_days.append(ad)
            print(ten_days)
        elif ad.current <= 5:
            five_days.append(ad)
        ad.myads_count = MyAds.objects.filter(adname=ad.AdName).aggregate(Sum('Count'))['Count__sum']
        ad.myads_count = ad.myads_count if ad.myads_count is not None else 0  # To Print the total count is 0

        if ad.myads_count is not None:  # To handle the total count is 0
            if ad.TotalCount:
                print(ad.AdName, ad.myads_count, ad.TotalCount)
                ad.percentage = (ad.myads_count / ad.TotalCount) * 100
            else:
                ad.percentage = 0
        else:
            ad.percentage = 0
    print(ten_days)
    return render(request, 'Fdashboard/dashboard.html', {'ads': ads, 'ten_days': ten_days, 'five_days': five_days})


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
        print(ad.AdName)
        # Prepare the data
        params = {
            'name': ad.AdName,
            'from': ad.StartDate.strftime("%Y-%m-%d"),
            'to': ad.EndDate.strftime("%Y-%m-%d"),
        }
        url = 'https://track.siliconharvest.net/get_adcount.php'  # Request url
        response = requests.get(url, params=params)
        if response.status_code != 200:
            # Log the error message for debugging purposes
            print(f"Error response received with status code {response.status_code}")
            continue
        try:
            data = response.json()
        except JSONDecodeError:
            # Log the error message for debugging purposes
            print(f"Error decoding JSON: {response.text}")
            continue
        data = response.json()
        if data is None:  # To handle if the data is not present
            print("API returned None")
            continue

        print(data)  # For Testing Purpose

        for item in data:  # Loop to store data in db
            imei = item.get('imei')
            AdName = ad.AdName
            for key, value in item.items():
                if key == 'imei':
                    continue
                day = key
                count = value
                try:
                    obj, created = MyAds.objects.update_or_create(adname=AdName, imei=imei, Count=count, date_time=day)
                except Exception as e:
                    logger.error("Error creating or updating MyAds object: %s", e)
        print(len(data))
    return render(request, 'Fdashboard/dashboard.html', {'ads': ads})
