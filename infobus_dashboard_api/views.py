import json

import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum
from utility.models import Ads
from utility.models import MyAds
from django.utils import timezone
from datetime import timedelta, date, datetime
import logging
from json.decoder import JSONDecodeError
import datetime as dt
from collections import defaultdict
from requests.exceptions import Timeout

logger = logging.getLogger(__name__)
# Create your views here.
timeout = 100


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
            # Return a JSON response with a success message
            return JsonResponse({'success': True, 'message': 'Logged in successfully'})
        else:
            # Return a JSON response with an error message
            return JsonResponse({'success': False, 'message': 'Username or password is incorrect'})

    return render(request, 'common/login.html')


def customer_view(request):
    if request.method == 'POST':
        ad_name = request.POST.get('ad_name')
        ad_name_upper = ad_name.upper()  # Convert ad_name to uppercase
        try:
            ad = Ads.objects.get(AdNameUsername=ad_name_upper)
        except Ads.DoesNotExist:
            messages.error(request, f"Ad with name {ad_name_upper} does not exist.")
            print('not fount')
            return redirect('customer-view')

        # rest of the view logic
        ad = Ads.objects.get(AdNameUsername=ad_name_upper)
        ad.myads_count = MyAds.objects.filter(adname=ad.AdName).aggregate(Sum('Count'))['Count__sum']
        ad.myads_count = ad.myads_count if ad.myads_count is not None else 0  # To Print the total count is 0

        day = timezone.now().date() - timedelta(days=1)
        today = date.today()
        yesterday = day.strftime("%Y-%m-%d")
        total_count_yesterday = \
        MyAds.objects.filter(adname=ad.AdName, date_time__contains=yesterday).aggregate(Sum('Count'))['Count__sum'] or 0
        if not total_count_yesterday:
            total_count_yesterday = 0
        # print(myad)
        # print(bus_nos)
        # print(total_count_yesterday, yesterday)

        # Fetch API data and give inital data
        params1 = {
                'name': ad.AdNameUsername,
                'from': today.strftime("%Y-%m-%d"),
                'length': 1,
            }
        urls = [
                'https://delta.busads.in/get_adcountv3.php',
                'https://track.siliconharvest.net/get_adcountv3.php',
                'https://tvl.busads.in/get_adcountv3.php']
        api_data = 0

        for url in urls:
            try:
                response = requests.get(url, params=params1, timeout=timeout)
                if response.status_code != 200:
                    print(f"Error response received with status code {response.status_code}")
                    logger.error(f"Error response received with status code {response.status_code}")
                    continue
                api_data += int(response.json())
            except Timeout:
                print(f"Timeout error while making request to {url}")
                logger.error(f"Timeout error while making request to {url}")
                continue
            except Exception as e:
                print(f"Error while making request to {url}: {e}")
                logger.error(f"Error while making request to {url}: {e}")
                continue

        # Create a dictionary with the result
        today_count = api_data

        # Convert dictionary to JSON
        json_data = json.dumps(today_count)


        if ad.myads_count is not None:  # To handle the total count is 0
            if ad.TotalCount:
                # print(ad.AdName, ad.myads_count, ad.TotalCount)
                ad.percentage = (ad.myads_count / ad.TotalCount) * 100
            else:
                ad.percentage = 0
        else:
            ad.percentage = 0


        params2 = {
            'name': ad.AdNameUsername,
            'from': today.strftime("%Y-%m-%d"),
            'length': 0,
        }

        # fetch count data from API
        url1 = 'https://track.siliconharvest.net/get_adcountv2.php'
        response1 = requests.get(url1, params2, timeout=timeout)
        try:
            data1 = response1.json()
        except ValueError:
            data1 = []
            logger.warning('Value error')
        except requests.exceptions.Timeout:
            logger.warning('Timeout error for {}'.format(url1))

        url2 = 'https://delta.busads.in/get_adcountv2.php'
        response2 = requests.get(url2, params2, timeout=timeout)
        try:
            data2 = response2.json()
        except ValueError:
            data2 = []
            logger.warning('Value error')
        except requests.exceptions.Timeout:
            logger.warning('Timeout error for {}'.format(url2))

        url3 = 'https://tvl.busads.in/get_adcountv2.php'
        response3 = requests.get(url3, params2, timeout=timeout)
        try:
            data3 = response3.json()
        except ValueError:
            data3 = []
            logger.warning('Value error')
        except requests.exceptions.Timeout:
            logger.warning('Timeout error for {}'.format(url3))

        # Extract required information from data1 and data2
        result = []
        for api__data in [data1, data2, data3]:
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

        context = {
            'ad': ad,
            'result': result,
            'yesterday': total_count_yesterday,
            'data': json_data,
        }
        return render(request, 'customer/detail.html', context)

    # If request method is not POST, render the form
    return render(request, 'customer/login.html')
