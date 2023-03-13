from django.shortcuts import render, redirect
from .forms import OfficeForm, OfficeUserForm
from django.contrib.auth.models import Group
from utility.models import District, Ads, MyAds
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
import logging
import requests
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from datetime import timedelta, date, datetime
from json.decoder import JSONDecodeError
from django.utils import timezone
from requests.exceptions import Timeout
from collections import defaultdict
import datetime as dt
import json

logger = logging.getLogger(__name__)
# Set the timeout value to 5 seconds
timeout = 200


# Create your views here.
def is_office(user):
    return user.groups.filter(name='Office').exists()


@login_required()
@user_passes_test(is_office)
def dashboard(request):
    district = District.objects.all().filter(is_Active=True)
    dist = request.GET.get('district')
    district_data = None
    if dist and dist.lower() != 'all':
        ads = Ads.objects.all().filter(District=dist)
        ten_days = []
        five_days = []
        for ad in ads:
            if ad.diff <= 10 and ad.diff >= 5:
                ten_days.append(ad)
                # print(ten_days)
            elif ad.diff <= 5:
                five_days.append(ad)
                # print(five_days)

            ad.myads_count = \
                MyAds.objects.filter(adname=ad.AdName, date_time__range=[ad.StartDate, ad.EndDate]).aggregate(
                    Sum('Count'))[
                    'Count__sum']

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
    else:
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

            ad.myads_count = \
                MyAds.objects.filter(adname=ad.AdName, date_time__range=[ad.StartDate, ad.EndDate]).aggregate(
                    Sum('Count'))[
                    'Count__sum']

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

    context = {
        'district': district,
        'ads': ads,
        'ten_days': ten_days,
        'five_days': five_days,
        'selected_district': dist
    }
    return render(request, 'office/dashboard.html', context)


@login_required()
@user_passes_test(is_office)
def view_ad(request, ad_id):
    ad = Ads.objects.get(id=ad_id)
    ad.myads_count = MyAds.objects.filter(adname=ad.AdName).aggregate(Sum('Count'))['Count__sum']
    ad.myads_count = ad.myads_count if ad.myads_count is not None else 0  # To Print the total count is 0

    day = timezone.now().date() - timedelta(days=1)
    today = date.today()
    # To get last 7 days data by default
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)
    start_str = start_date.strftime('%d/%m/%y')
    end_str = end_date.strftime('%d/%m/%y')

    param = {
        'name': ad.AdNameUsername,
        'from': start_date.strftime("%Y-%m-%d"),
        'to': end_date.strftime("%Y-%m-%d"),
    }
    # Query the MyAds model to get the required data
    urls = ['https://delta.busads.in/get_adcountv2.php', 'https://track.siliconharvest.net/get_adcountv2.php',
            'https://tvl.busads.in/get_adcountv2.php']
    for url in urls:
        response = requests.get(url, params=param, timeout=timeout)
        if response.status_code != 200:
            print(f"Error response received with status code {response.status_code}")
            logger.error(f"Error response received with status code {response.status_code}")
            continue
        try:
            data = response.json()
        except JSONDecodeError:
            print(f"Error decoding JSON: {response.text}")
            logger.warning(f"Error decoding JSON: {response.text}")
            continue
        except Timeout:
            print("Request TimeOut")
            logger.error(f"Timeout Error: {url}")
            continue
        if data is None:
            print("API returned None")
            logger.warning('API returned None')
            continue

        day_counts = defaultdict(int)

        for item in data:
            for key, value in item.items():
                if key in ['imei', 'bus_no', 'route_no', 'route_name']:
                    continue
                day = dt.datetime.strptime(key, "%d/%m/%Y").date().strftime("%d/%m")
                count = int(value)
                day_counts[day] += count

        date_count_array = [{'date': date, 'count': count} for date, count in day_counts.items()]

    # print(date_count_array)

    if ad.myads_count is not None:  # To handle the total count is 0
        if ad.TotalCount:
            # print(ad.AdName, ad.myads_count, ad.TotalCount)
            ad.percentage = (ad.myads_count / ad.TotalCount) * 100
        else:
            ad.percentage = 0
    else:
        ad.percentage = 0

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

    labels = []
    data = []
    for item in date_count_array:
        labels.append(item['date'])
        data.append(item['count'])
    context = {
        'ad': ad,
        'result': result,
        'json_data': json_data,
        'labels': labels,
        'data': data,
        'start_date': start_str,
        'end_date': end_str
    }
    return render(request, 'office/detail.html', context)


def Office_signup_view(request):
    userForm = OfficeForm()
    OfficeUser = OfficeUserForm()
    mydict = {'userForm': userForm, 'OfficeUser': OfficeUser}
    if request.method == 'POST':
        userForm = OfficeForm(request.POST)
        OfficeUser = OfficeUserForm(request.POST)
        if userForm.is_valid() and OfficeUser.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            office_user = OfficeUser.save(commit=False)
            office_user.user = user
            office_user.save()
            my_group = Group.objects.get_or_create(name='Office')
            my_group[0].user_set.add(user)
        return redirect('Office:Office-login')
    return render(request, 'office/signup.html', context=mydict)


@login_required()
@user_passes_test(is_office)
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to maintain user session
            messages.success(request, 'Your password was successfully updated!')
            return redirect('Office:office-dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(user=request.user)
    context = {'form': form}
    return render(request, 'common/change_password.html', context)
