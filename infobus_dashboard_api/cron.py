from json import JSONDecodeError
import datetime as dt
import logging
import requests
from requests import Timeout
from api.District.models import District
from api.ads.models import Ads
from dashboard.models import MyAds
from utility.models import bus_Detail

timeout = 100
logger = logging.getLogger(__name__)


def getupdate():
    try:
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
        print('succes')
        return "getupdate Task completed successfully"
    except Exception as e:
        raise


def getstatus(request):
    urls = ['https://delta.busads.in/get_status.php',
            'https://track.siliconharvest.net/get_status.php',
            'https://tvl.busads.in/get_status.php']
    error_messages = []
    for url in urls:
        response = requests.get(url)
        if response.status_code != 200:
            # Log the error message for debugging purposes
            error_messages.append(f"Error response received with status code {response.status_code} from {url}")
            continue
        try:
            data = response.json()
        except JSONDecodeError:
            # Log the error message for debugging purposes
            error_messages.append(f"Error decoding JSON from getstatus: {response.text}")
            continue
        if data is None:  # To handle if the data is not present
            error_messages.append(f"API returned None getstatus from  {url}")
            continue
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

        print(f"Data retrieved from {url} and stored in the database")

    if error_messages:
        return ", ".join(error_messages)
    else:
        return "Data retrieved from URLs and stored in the database"
