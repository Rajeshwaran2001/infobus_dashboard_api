import requests
from celery.app import task
from django.http import response

from api.ads.models import Ads
from dashboard.models import MyAds


@task
def send_data_to_api():
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
