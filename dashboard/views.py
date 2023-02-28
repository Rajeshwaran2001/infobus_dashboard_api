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
from .models import MyAds, Franchise
import datetime as dt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from datetime import timedelta, date, datetime
from utility.models import bus_Detail
import os
import pandas as pd


logger = logging.getLogger(__name__)


# Create your views here.
def is_patner(user):
    return user.groups.filter(name='Franchise').exists()


@login_required()
@user_passes_test(is_patner)
def dash(request):
    # Get the current user's franchise and district
    franchise = Franchise.objects.get(user=request.user)
    districts = franchise.district.all()  # get all associated districts
    ads = Ads.objects.filter(District__in=districts).distinct()
    # print(districts, ads)
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
    ad.myads_count = MyAds.objects.filter(adname=ad.AdName).aggregate(Sum('Count'))['Count__sum']
    ad.myads_count = ad.myads_count if ad.myads_count is not None else 0  # To Print the total count is 0
    day = timezone.now().date() - timedelta(days=1)
    today = date.today()
    yesterday = day.strftime("%d/%m/%Y")
    # To get last 7 days data by default
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)

    end_date_str = end_date.strftime("%d/%m/%Y")
    start_date_str = start_date.strftime("%d/%m/%Y")

    print(end_date_str)
    print(start_date_str)
    # Query the MyAds model to get the required data
    last_7_day = MyAds.objects.filter(adname=ad.AdName, date_time__range=(start_date_str, end_date_str)).values(
        'date_time').annotate(count=Sum('Count'))
    ad_counts_array = []
    for ad_count in last_7_day:
        ad_counts_array.append({'count': ad_count['count'], 'date': ad_count['date_time']})

    # print(ad_counts_array)

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
    today_count = result

    # Convert dictionary to JSON
    json_data = json.dumps(today_count)

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

    # Extract required information from data1 and data2
    result = []
    for api__data in [data1, data2]:
        for item in api__data:
            for key, value in item.items():
                if key != 'imei' and key != 'bus_no' and key != 'route_no' and key != 'route_name':
                    d = {
                        'imei': item['imei'],
                        'bus_no': item['bus_no'],
                        'route_no': item['route_no'],
                        'route_name': item['route_name'],
                        'date': key,
                        'count': value,
                    }
                    result.append(d)

    labels = []
    data = []
    for item in ad_counts_array:
        labels.append(item['date'])
        data.append(item['count'])
    context = {
        'ad': ad,
        'result': result,
        'json_data': json_data,
        'labels': labels,
        'data': data,
        'start_date_str': start_date_str,
        'end_date_str': end_date_str,
    }
    return render(request, 'Fdashboard/detail.html', context)

@login_required()
@user_passes_test(is_patner)
def route_summary(request):
    csv_path = os.path.join(os.getcwd(), 'static', 'book.xls')
    sheets = pd.read_excel(csv_path, sheet_name=None)
    # Replace NaN with empty strings
    sheets = {sheet_name: sheet_data.fillna('') for sheet_name, sheet_data in sheets.items()}
    context = {
        'sheets': sheets,
    }
    return render(request, 'Fdashboard/route.html', context)

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
            # get the selected districts and add them to the FranchiseUser object
            selected_districts = FranchiseUser.cleaned_data.get('district')
            Franchise.save()
            Franchise.district.add(*selected_districts)
            my_group = Group.objects.get_or_create(name='Franchise')
            my_group[0].user_set.add(user)
        return redirect('FDashboard:Flogin')
    return render(request, 'Fdashboard/signup.html', context=mydict)


def getupdate(request):
    ads = Ads.objects.all()
    unique_cities = bus_Detail.objects.values_list('city', flat=True).distinct()
    print(unique_cities)
    for city in unique_cities:
        district, created = District.objects.get_or_create(District=city)
        if not created:
            print(f"District '{city}' already exists")
        else:
            print(f"District '{city}' created")
    for ad in ads:
        params = {
            'name': ad.AdName,
            'from': ad.StartDate.strftime("%Y-%m-%d"),
            'to': ad.EndDate.strftime("%Y-%m-%d"),
        }
        urls = ['https://delta.busads.in/get_adcountv2.php', 'https://track.siliconharvest.net/get_adcountv2.php']
        for url in urls:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"Error response received with status code {response.status_code}")
                continue
            try:
                data = response.json()
            except JSONDecodeError:
                print(f"Error decoding JSON: {response.text}")
                continue
            if data is None:
                print("API returned None")
                continue
            for item in data:
                imei = item.get('imei')
                AdName = ad.AdName
                bus_no = item.get('bus_no')
                route_no = item.get('route_no')
                route_name = item.get('route_name')
                for key, value in item.items():
                    if key in ['imei', 'bus_no', 'route_no', 'route_name']:
                        continue
                    day = dt.datetime.strptime(key, "%d/%m/%Y").date().strftime("%d/%m/%Y")
                    count = value
                    try:
                        obj, created = MyAds.objects.update_or_create(adname=AdName, imei=imei, date_time=day, bus_no=bus_no, route_no=route_no, route_name=route_name, defaults={'Count': count})
                    except Exception as e:
                        print("Error creating or updating MyAds object: %s", e)

    return render(request, 'apitest/ff.html', {'ads': ads})


def update_today_count(request):
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

def update_bus_count(request):
    today = date.today()
    ad_name = request.GET.get('ad_name')
    params = {
        'name': ad_name,
        'from': today.strftime("%Y-%m-%d"),
        'length': 0,
    }

    # fetch count data from API
    url1 = 'https://track.siliconharvest.net/get_adcountv2.php'
    response1 = requests.get(url1, params)
    try:
        data1 = response1.json()
    except ValueError:
        data1 = []

    url2 = 'https://delta.busads.in/get_adcountv2.php'
    response2 = requests.get(url2, params)
    try:
        data2 = response2.json()
    except ValueError:
        data2 = []

    # Extract required information from data1 and data2
    result = []
    for data in [data1, data2]:
        for item in data:
            for key, value in item.items():
                if key != 'imei' and key != 'bus_no' and key != 'route_no' and key != 'route_name':
                    d = {
                        'bus_no': item['bus_no'],
                        'route_no': item['route_no'],
                        'route_name': item['route_name'],
                        'date': key,
                        'count': value,
                    }
                    result.append(d)
    return JsonResponse(result, safe=False)

def get_data(request):
    if request.method == "POST":
        # Get the request data as bytes
        request_body = request.body

        # Parse the JSON data into a dictionary
        data = json.loads(request_body)

        # Access the start_date, end_date, and ad_name values
        start_date = data["start_date"]
        end_date = data["end_date"]
        ad_name = data["ad_name"]
        print(start_date,end_date,ad_name)

        data = MyAds.objects.filter(adname=ad_name, date_time__range=(start_date, end_date)).values(
            'date_time').annotate(count=Sum('Count'))
        data_array = []
        for ad_count in data:
            data_array.append({'count': ad_count['count'], 'date': ad_count['date_time']})

        labels2 = []
        data2 = []
        for item in data_array:
            labels2.append(item['date'])
            data2.append(item['count'])
            # Create a dictionary with labels2 and data2
        chart_data = {'labels': labels2, 'data': data2}
        #print(chart_data)

        # Return the chart_data as a JSON response
        return JsonResponse(chart_data)
