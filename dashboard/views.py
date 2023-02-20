import json
import logging
from json.decoder import JSONDecodeError
import requests
from django.contrib.auth.models import Group
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect
from api.ads.models import Ads
from api.District.models import District
from dashboard.forms import FranchiseForm, FranchiseUserForm
from .models import MyAds
from utility.models import bus_Detail
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from datetime import timedelta, date, datetime

logger = logging.getLogger(__name__)


# Create your views here.
def is_patner(user):
    return user.groups.filter(name='Franchise').exists()


@login_required()
@user_passes_test(is_patner)
def dash(request):
    ads = Ads.objects.all()
    ten_days = []
    five_days = []
    for ad in ads:
        if ad.diff <= 10 and ad.diff >= 5:
            ten_days.append(ad)
            # print(ten_days)
        elif ad.diff <= 5:
            five_days.append(ad)
            # print(five_days)
        ad.myads_count = MyAds.objects.filter(adname=ad.AdName).aggregate(Sum('Count'))['Count__sum']
        ad.myads_count = ad.myads_count if ad.myads_count is not None else 0  # To Print the total count is 0
        statuss = ad.day * ad.ECPD
        diff = abs(ad.myads_count - statuss)
        if ad.myads_count == 0:
            ad.status = "crtical"
        elif diff == 0:
            ad.status = "up"
        elif diff <= 200:
            ad.status = "up"
        elif diff > 200 and diff <= 400:
            ad.status = "down"
        elif ad.myads_count > statuss:
            ad.status = "up"
        else:
            ad.status = "error"

        # print(ad.day, ad.ECPD, statuss, ad.status, diff)
        if ad.myads_count is not None:  # To handle the total count is 0
            if ad.TotalCount:
                # print(ad.AdName, ad.myads_count, ad.TotalCount)
                ad.percentage = (ad.myads_count / ad.TotalCount) * 100
            else:
                ad.percentage = 0
        else:
            ad.percentage = 0
    # getupdate(request)
    return render(request, 'Fdashboard/dashboard.html', {'ads': ads, 'ten_days': ten_days, 'five_days': five_days})


@login_required()
@user_passes_test(is_patner)
def view_ad(request, ad_id):
    ad = Ads.objects.get(id=ad_id)
    myad = MyAds.objects.filter(adname=ad.AdName).values_list('imei', flat=True).distinct()
    bus_nos = bus_Detail.objects.filter(imei__in=myad).values_list('bus_no', 'route_no').distinct().order_by()
    ad.myads_count = MyAds.objects.filter(adname=ad.AdName).aggregate(Sum('Count'))['Count__sum']
    ad.myads_count = ad.myads_count if ad.myads_count is not None else 0  # To Print the total count is 0
    day = timezone.now().date() - timedelta(days=1)
    today = date.today()
    yesterday = day.strftime("%#d/%#m/%Y")
    total_count_yesterday = MyAds.objects.filter(adname=ad.AdName, date_time__contains=yesterday).aggregate(Sum('Count'))['Count__sum'] or 0
    if not total_count_yesterday:
        total_count_yesterday = 0
    # print(myad)
    # print(bus_nos)
    # print(total_count_yesterday, yesterday)

    if ad.myads_count is not None:  # To handle the total count is 0
        if ad.TotalCount:
            # print(ad.AdName, ad.myads_count, ad.TotalCount)
            ad.percentage = (ad.myads_count / ad.TotalCount) * 100
        else:
            ad.percentage = 0
    else:
        ad.percentage = 0

    # Fetch API data and give inital data
    params = {
        'name': ad.AdName,
        'from': today.strftime("%Y-%m-%d"),
        'length': 1,
    }
    url1 = 'https://delta.busads.in/get_adcountv2.php'
    api_data = requests.get(url1, params=params).json()
    url2 = 'https://track.siliconharvest.net/get_adcountv2.php'
    api_data2 = requests.get(url2, params=params).json()

    # Print API responses to console
    # print(api_data)
    # print(api_data2)

    # Add the two API responses
    result = int(api_data) + int(api_data2)

    # Create a dictionary with the result
    data = result

    # Convert dictionary to JSON
    json_data = json.dumps(data)

    params2 = {
        'name': ad.AdName,
        'from': today.strftime("%Y-%m-%d"),
        'length': 0,
    }

    # fetch count data from API
    url1 = 'https://track.siliconharvest.net/get_adcountv2.php'
    response1 = requests.get(url1, params2)
    try:
        data1 = response1.json()
    except ValueError:
        data1 = []

    url2 = 'https://delta.busads.in/get_adcountv2.php'
    response2 = requests.get(url2, params2)
    try:
        data2 = response2.json()
    except ValueError:
        data2 = []

    # extract IMEI values from both API responses
    imei_values = [obj['imei'] for obj in data1] + [obj['imei'] for obj in data2]

    # match IMEI with bus_nos in Django model
    bus_nosa = bus_Detail.objects.filter(imei__in=imei_values).values_list('bus_no', 'route_no').distinct()

    # extract values for the matching date key for both API responses
    values = []
    date_format = '%d/%m/%Y'
    for obj in data1 + data2:
        for key in obj:
            try:
                date_value = datetime.strptime(key, date_format).date()
                if date_value:
                    values.append(obj[key])
                    break
            except ValueError:
                pass

    # if values is empty, set it to [0]
    if not values:
        values = [0]

    # create dictionary of bus_no to values
    bus_to_values = {}
    for bus_no, route_no in bus_nos:
        bus_to_values[bus_no] = values

    mylist = zip(myad, bus_nos, values)

    context = {
        'ad': ad,
        'mylist': mylist,
        'yesterday': total_count_yesterday,
        'data': json_data,
    }
    return render(request, 'Fdashboard/detail.html', context)


def Franchise_signup_view(request):
    userForm = FranchiseForm()
    FranchiseUser = FranchiseUserForm()
    dist = District.objects.all().filter(is_Active=True)
    mydict = {'userForm': userForm, 'FranchiseUser': FranchiseUser, 'dist': dist}
    if request.method == 'POST':
        userForm = FranchiseForm(request.POST)
        FranchiseUser = FranchiseUserForm(request.POST, request.FILES)
        if userForm.is_valid() and FranchiseUser.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            Franchise = FranchiseUser.save(commit=False)
            Franchise.user = user
            Franchise.photo = FranchiseUser.cleaned_data.get('photo')
            Franchise.save()
            my_group = Group.objects.get_or_create(name='Franchise')
            my_group[0].user_set.add(user)
        return redirect('FDashboard:Flogin')
    return render(request, 'Fdashboard/signup.html', context=mydict)


def getupdate(request):
    ads = Ads.objects.all()
    for ad in ads:  # Loop ads
        # print(ad.AdName)
        # Prepare the data
        params = {
            'name': ad.AdName,
            'from': ad.StartDate.strftime("%Y-%m-%d"),
            'to': ad.EndDate.strftime("%Y-%m-%d"),
        }
        url = 'https://delta.busads.in/get_adcountv2.php'  # Request url
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

        #  print(data)  # For Testing Purpose

        for item in data:  # Loop to store data in db
            imei = item.get('imei')
            AdName = ad.AdName
            for key, value in item.items():
                if key == 'imei':
                    continue
                day = key
                #  date_time = dt.datetime.strptime(day, "%Y-%m-%d").strftime("%d/%m/%Y")
                count = value
                try:
                    obj, created = MyAds.objects.update_or_create(adname=AdName, imei=imei, date_time=day,
                                                                  defaults={'Count': count})
                except Exception as e:
                    logger.error("Error creating or updating MyAds object: %s", e)

        # Make another API call
        url2 = 'https://track.siliconharvest.net/get_adcountv2.php'
        response2 = requests.get(url2, params=params)
        if response2.status_code != 200:
            # Log the error message for debugging purposes
            print(f"Error response received with status code {response2.status_code}")
            continue
        try:
            data2 = response2.json()
        except JSONDecodeError:
            # Log the error message for debugging purposes
            print(f"Error decoding JSON: {response2.text}")
            continue
        data2 = response2.json()
        if data2 is None:  # To handle if the data is not present
            print("API returned None")
            continue

        #  print(data2)  # For Testing Purpose

        for item2 in data2:  # Loop to store data in db
            imei = item2.get('imei')
            AdName = ad.AdName
            for key, value in item2.items():
                if key == 'imei':
                    continue
                day = key
                #  date_time = dt.datetime.strptime(day, "%Y-%m-%d").strftime("%d/%m/%Y")
                count = value
                try:
                    obj, created = MyAds.objects.update_or_create(adname=AdName, imei=imei, date_time=day,
                                                                  defaults={'Count': count})
                except Exception as e:
                    logger.error("Error creating or updating MyAds object: %s", e)

    #   print(len(data))
    return render(request, 'apitest/ff.html', {'ads': ads})


def api_view(request):
    today = date.today()
    ad_name = request.GET.get('ad_name')
    params = {
        'name': ad_name,
        'from': today.strftime("%Y-%m-%d"),
        'length': 1,
    }

    # Fetch API data
    url1 = 'https://delta.busads.in/get_adcountv2.php'
    api_data1 = requests.get(url1, params=params).json()
    url2 = 'https://track.siliconharvest.net/get_adcountv2.php'
    api_data2 = requests.get(url2, params=params).json()
    print(api_data1, api_data2)

    # Print API responses to console
    # print(api_data)
    # print(api_data2)

    # Add the two API responses
    result = int(api_data1) + int(api_data2)

    # Create a dictionary with the result
    data = result

    # Convert dictionary to JSON
    json_data = json.dumps(data)

    # Return JSON response
    return JsonResponse(json_data, safe=False)
