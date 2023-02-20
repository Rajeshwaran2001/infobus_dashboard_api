from django.shortcuts import render
import logging
from json.decoder import JSONDecodeError
import requests
from .models import bus_Detail

# Create your views here.

logger = logging.getLogger(__name__)


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
                                                           station=station, position=position,
                                                           defaults={'imei': imei, 'route_name': route_name,
                                                                     'route_no': route_no, 'station': station,
                                                                     'position':position, 'bus_no': bus_no,
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

    return render(request, 'apitest/ff.html')
