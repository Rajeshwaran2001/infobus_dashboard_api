import datetime as dt
import json
import logging
from collections import defaultdict
from json.decoder import JSONDecodeError
from datetime import timedelta, date, datetime
import requests
from django.http import JsonResponse
from django.shortcuts import render
from requests.exceptions import Timeout

from .models import Ads, District, MyAds, bus_Detail

# Create your views here.

logger = logging.getLogger(__name__)
# Set the timeout value to 5 seconds
timeout = 200


def fetch_and_store_data(url):
    response = requests.get(url)
    if response.status_code != 200:
        # Log the error message for debugging purposes
        print(f"Error response received with status code {response.status_code}")
    try:
        data = response.json()
    except JSONDecodeError:
        # Log the error message for debugging purposes
        print(f"Error decoding JSON: {response.text}")
    data = response.json()
    if data is None:  # To handle if the data is not present
        print("API returned None")
    #  print(data)  # For Testing Purpose

    for item in data:  # Loop to store data in db
        bus_no = item.get('bus_no')
        city = item.get('city')
        depo = item.get('depo')
        route_no = item.get('route_no')
        route_name = item.get('route_name')
        imei = item.get('imei')
        station = item.get('station')
        position = item.get('position')
        obj, created = bus_Detail.objects.update_or_create(bus_no=bus_no, city=city, depo=depo,
                                                           route_no=route_no, route_name=route_name, imei=imei,
                                                           defaults={'imei': imei, 'route_name': route_name,
                                                                     'route_no': route_no, 'bus_no': bus_no,
                                                                     'depo': depo, 'city': city})

    #   print(len(data))
    return data


def getstatus(request):
    url1 = 'https://delta.busads.in/get_status.php'
    data1 = fetch_and_store_data(url1)
    if isinstance(data1, str):  # Check if an error message was returned
        print(data1)  # Log the error message for debugging purposes
    else:
        # Data was successfully stored, do something with it
        print(f"Data retrieved from {url1} and stored in the database")

    url2 = 'https://track.siliconharvest.net/get_status.php'
    data2 = fetch_and_store_data(url2)
    if isinstance(data2, str):  # Check if an error message was returned
        print(data2)  # Log the error message for debugging purposes
    else:
        # Data was successfully stored, do something with it
        print(f"Data retrieved from {url2} and stored in the database")

    url3 = 'https://tvl.busads.in/get_status.php'
    data3 = fetch_and_store_data(url3)
    if isinstance(data3, str):  # Check if an error message was returned
        print(data3)  # Log the error message for debugging purposes
    else:
        # Data was successfully stored, do something with it
        print(f"Data retrieved from {url3} and stored in the database")

    return render(request, 'apitest/ff.html')


def getupdate(request):
    ads = Ads.objects.all()
    unique_cities = bus_Detail.objects.values_list('city', flat=True).distinct()
    for city in unique_cities:
        districts = District.objects.filter(District=city)
        if districts.exists():
            print(f"{districts.count()} districts already exist for '{city}'")
        else:
            district = District.objects.create(District=city)
            print(f"District '{district}' created")
    for ad in ads:
        params = {
            'name': ad.AdNameUsername,
            'from': ad.StartDate.strftime("%Y-%m-%d"),
            'to': ad.EndDate.strftime("%Y-%m-%d"),
        }
        urls = ['https://delta.busads.in/get_adcountv3.php', 'https://track.siliconharvest.net/get_adcountv3.php',
                'https://tvl.busads.in/get_adcountv3.php']
        for url in urls:
            response = requests.get(url, params=params, timeout=timeout)
            if response.status_code != 200:
                print(f"Error response received with status code {response.status_code}")
                logger.error(f"Error response received with status code {response.status_code}")
                continue
            try:
                data = response.json()
            except JSONDecodeError:
                print(f"Error decoding JSON: {response.text}")
                continue
            except Timeout:
                print("Request TimeOut")
                logger.error(f"Timeout Error: {url}")
            if data is None:
                print("API returned None")
                continue
            for item in data:
                imei = item.get('imei')
                AdName = ad.AdName
                bus_no = item.get('bus_no')
                for key, value in item.items():
                    if key in ['imei', 'bus_no']:
                        continue
                    day = dt.datetime.strptime(key, "%d/%m/%Y").date().strftime("%Y-%m-%d")
                    count = value
                    try:
                        obj, created = MyAds.objects.update_or_create(adname=AdName, imei=imei, date_time=day,
                                                                      bus_no=bus_no, defaults={'Count': count})
                    except Exception as e:
                        print("Error creating or updating MyAds object: %s", e)
                        logger.error("Error creating or updating MyAds object: %s", e)

    return render(request, 'apitest/ff.html', {'ads': ads})


def update_today_count(request):
    today = date.today()
    ad_name = request.GET.get('ad_name')
    params = {
        'name': ad_name,
        'from': today.strftime("%Y-%m-%d"),
        'length': 1,
    }

    urls = ['https://delta.busads.in/get_adcountv3.php', 'https://track.siliconharvest.net/get_adcountv3.php',
            'https://tvl.busads.in/get_adcountv3.php']
    api_data = 0

    for url in urls:
        try:
            response = requests.get(url, params=params, timeout=timeout)
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
    data = api_data

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
    url1 = 'https://track.siliconharvest.net/get_adcountv3.php'
    response1 = requests.get(url1, params, timeout=timeout)
    try:
        data1 = response1.json()
    except ValueError:
        data1 = []
        logger.warning('Value error')
    except requests.exceptions.Timeout:
        logger.warning('Timeout error for {}'.format(url1))

    url2 = 'https://delta.busads.in/get_adcountv3.php'
    response2 = requests.get(url2, params, timeout=timeout)
    try:
        data2 = response2.json()
    except ValueError:
        data2 = []
        logger.warning('Value error')
    except requests.exceptions.Timeout:
        logger.warning('Timeout error for {}'.format(url2))

    url3 = 'https://tvl.busads.in/get_adcountv3.php'
    response3 = requests.get(url3, params, timeout=timeout)
    try:
        data3 = response3.json()
    except ValueError:
        data3 = []
        logger.warning('Value error')
    except requests.exceptions.Timeout:
        logger.warning('Timeout error for {}'.format(url3))

    # Extract required information from data1 and data2
    result = []
    for data in [data1, data2, data3]:
        for item in data:
            for key, value in item.items():
                if key != 'imei' and key != 'bus_no':
                    d = {
                        'bus_no': item['bus_no'],
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
        print(start_date, end_date, ad_name)

        param = {
            'name': ad_name,
            'from': start_date,
            'to': end_date,
        }
        # Query the MyAds model to get the required data
        urls = ['https://delta.busads.in/get_adcountv3.php', 'https://track.siliconharvest.net/get_adcountv3.php',
                'https://tvl.busads.in/get_adcountv3.php']
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
                continue
            except Timeout:
                print(f"Error Timeout: {url}")
            if data is None:
                print("API returned None")
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

        labels2 = []
        data2 = []
        for item in date_count_array:
            labels2.append(item['date'])
            data2.append(item['count'])
            # Create a dictionary with labels2 and data2
        chart_data = {'labels': labels2, 'data': data2}
        # print(chart_data)

        # Return the chart_data as a JSON response
        return JsonResponse(chart_data)
