import requests
from celery.app import task
from django.http import response

from api.ads.models import Ads


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
        url = requests.get('https://track.siliconharvest.net/get_adcount.php', params=params)  # Request data
        data = url.json()
        print(data)  # For Testing Purpose

        # Check the response status code
        if response.status_code == 200:
            imei = data.get("imei")


