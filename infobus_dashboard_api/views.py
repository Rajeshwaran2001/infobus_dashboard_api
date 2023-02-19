import requests
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum
from api.ads.models import Ads
from dashboard.models import MyAds
from utility.models import bus_Detail
from django.utils import timezone
from datetime import timedelta, date
import json

# Create your views here.


def is_patner(user):
    return user.groups.filter(name='Franchise').exists()


def is_office(user):
    return user.groups.filter(name='Office').exists()


def afterlogin_view(request):
    if is_patner(request.user):
        return redirect('FDashboard:dashboard')
    elif is_office(request.user):
        return redirect('FDashboard:dashboard')
    else:
        return redirect('Login')


def logout_user(request):
    logout(request)
    return redirect('Login')


def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('afterlogin')
        else:
            messages.error(request, "Username Or Password is incorrect!!",
                           extra_tags='alert alert-warning alert-dismissible fade show')

    return render(request, 'common/login.html')


def customer_view(request):
    if request.method == 'POST':
        ad_name = request.POST.get('ad_name')
        ad_name_upper = ad_name.upper()  # Convert ad_name to uppercase
        try:
            ad = Ads.objects.get(AdName=ad_name_upper)
        except Ads.DoesNotExist:
            messages.error(request, f"Ad with name {ad_name_upper} does not exist.", extra_tags='alert alert-warning fade show')
            print('not fount')
            return redirect('customer-view')

        # rest of the view logic
        myad = MyAds.objects.filter(adname=ad.AdName).values_list('imei', flat=True).distinct()
        bus_nos = bus_Detail.objects.filter(imei__in=myad).values_list('bus_no', 'route_no').distinct()
        ad.myads_count = MyAds.objects.filter(adname=ad.AdName).aggregate(Sum('Count'))['Count__sum']
        ad.myads_count = ad.myads_count if ad.myads_count is not None else 0  # To Print the total count is 0
        day = timezone.now().date() - timedelta(days=1)
        today = date.today()
        yesterday = day.strftime("%#d/%#m/%Y")
        total_count_yesterday = MyAds.objects.filter(adname=ad.AdName, date_time__contains=yesterday).aggregate(Sum(
            'Count'))[
                                    'Count__sum'] or 0
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

        mylist = zip(myad, bus_nos)
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

        context = {
            'ad': ad,
            'mylist': mylist,
            'yesterday': total_count_yesterday,
            'data': json_data
        }
        return render(request, 'customer/detail.html', context)

    # If request method is not POST, render the form
    return render(request, 'customer/login.html')


