import csv
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
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from collections import defaultdict
import xlrd
import xlwt
from django.http import HttpResponse

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
    ads = Ads.objects.filter(District__in=districts).distinct().filter(display=True)

    csv_path = os.path.join(os.getcwd(), 'static', 'data')
    total_spots = 0  # initialize total to zero
    filled_spots = 0  # initialize total to zero
    last_modified = None  # initialize last modified time to None

    for district in districts:
        # Assuming that each district's Excel file is named after the district's name
        file_name = f"{district.District}_summary.csv"
        file_path = os.path.join(csv_path, file_name)

        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            row = next(reader)
            # Split column names by colon and extract parts
            total_col = row[0]  # get the first column name
            total_spots += int(total_col.split(':')[1])  # extract and add total spots
            filled_col = row[1]  # get the second column name
            filled_spots += int(filled_col.split(':')[1])  # extract and add filled spots

        # Get the last modified time of the file
        mod_time = os.path.getmtime(file_path)
        if last_modified is None or mod_time > last_modified:
            last_modified = mod_time

    # Convert the last modified time to a human-readable format
    last_modified_str = None
    if last_modified is not None:
        last_modified_str = datetime.fromtimestamp(last_modified).strftime('%d/%m/%y')

    # print(districts, ads)
    # print(last_modified)
    free = total_spots - filled_spots
    percentage = (filled_spots / total_spots) * 100
    # print(percentage)
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

    context = {
        'ads': ads,
        'ten_days': ten_days,
        'five_days': five_days,
        'total': total_spots,
        'filled': filled_spots,
        'free': free,
        'percentage': percentage,
        'last': last_modified_str
    }
    return render(request, 'Fdashboard/dashboard.html', context)


@login_required()
@user_passes_test(is_patner)
def view_ad(request, ad_id):
    ad = Ads.objects.get(id=ad_id)
    ad.myads_count = MyAds.objects.filter(adname=ad.AdName).aggregate(Sum('Count'))['Count__sum']
    ad.myads_count = ad.myads_count if ad.myads_count is not None else 0  # To Print the total count is 0
    # Get the current user's franchise and district
    franchise = Franchise.objects.get(user=request.user)
    districts = franchise.district.all()  # get all associated districts
    csv_path = os.path.join(os.getcwd(), 'static', 'data')
    total_spots = 0  # initialize total to zero
    filled_spots = 0  # initialize total to zero
    last_modified = None  # initialize last modified time to None

    for district in districts:
        # Assuming that each district's Excel file is named after the district's name
        file_name = f"{district.District}_summary.csv"
        file_path = os.path.join(csv_path, file_name)

        # Get the last modified time of the file
        mod_time = os.path.getmtime(file_path)
        if last_modified is None or mod_time > last_modified:
            last_modified = mod_time

    # Convert the last modified time to a human-readable format
    last_modified_str = None
    if last_modified is not None:
        last_modified_str = datetime.fromtimestamp(last_modified).strftime('%d/%m/%y')
    day = timezone.now().date() - timedelta(days=1)
    today = date.today()
    yesterday = day.strftime("%d/%m/%Y")
    # To get last 7 days data by default
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)
    start_str = start_date.strftime('%d/%m/%y')
    end_str = end_date.strftime('%d/%m/%y')

    param = {
        'name': ad.AdName,
        'from': start_date.strftime("%Y-%m-%d"),
        'to': end_date.strftime("%Y-%m-%d"),
    }
    # Query the MyAds model to get the required data
    urls = ['https://delta.busads.in/get_adcountv2.php', 'https://track.siliconharvest.net/get_adcountv2.php',
            'https://tvl.busads.in/get_adcountv2.php']
    for url in urls:
        response = requests.get(url, params=param)
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
        if data is None:
            print("API returned None")
            logger.warning('API returned None')
            continue
        day_counts = defaultdict(int)
        for item in data:
            for key, value in item.items():
                if key in ['imei', 'bus_no', 'route_no', 'route_name']:
                    continue
                day = dt.datetime.strptime(key, "%d/%m/%Y").date().strftime("%d/%m/%Y")
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
    params = {
        'name': ad.AdName,
        'from': today.strftime("%Y-%m-%d"),
        'length': 1,
    }
    url1 = 'https://delta.busads.in/get_adcountv2.php'
    api_data = requests.get(url1, params=params).json()
    url2 = 'https://track.siliconharvest.net/get_adcountv2.php'
    api_data2 = requests.get(url2, params=params).json()
    url3 = 'https://delta.busads.in/get_adcountv2.php'
    api_data3 = requests.get(url3, params=params).json()

    # Print API responses to console
    # print(api_data)
    # print(api_data2)

    # Add the two API responses
    result = int(api_data) + int(api_data2) + int(api_data3)

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
        logger.warning('Value error')

    url2 = 'https://delta.busads.in/get_adcountv2.php'
    response2 = requests.get(url2, params2)
    try:
        data2 = response2.json()
    except ValueError:
        data2 = []
        logger.warning('Value error')

    url3 = 'https://tvl.busads.in/get_adcountv2.php'
    response2 = requests.get(url3, params2)
    try:
        data3 = response2.json()
    except ValueError:
        data3 = []
        logger.warning('Value error')

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
        'last': last_modified_str,
        'start_date': start_str,
        'end_date': end_str
    }
    return render(request, 'Fdashboard/detail.html', context)


@login_required()
@user_passes_test(is_patner)
def route_summary(request):
    # Get the current user's franchise and district
    franchise = Franchise.objects.get(user=request.user)
    districts = franchise.district.all()  # get all associated districts

    # Construct the path to the Excel file based on the districts
    csv_path = os.path.join(os.getcwd(), 'static', 'data')
    sheets = {}  # initialize sheets as a dictionary

    for district in districts:
        # Assuming that each district's Excel file is named after the district's name
        file_name = f"{district.District}_filllist.xls"
        file_path = os.path.join(csv_path, file_name)

        try:
            # Open the Excel file using xlrd
            workbook = xlrd.open_workbook(file_path)
            # Replace NaN with empty strings
            sheets_district = {}
            for sheet_name in workbook.sheet_names():
                sheet = workbook.sheet_by_name(sheet_name)
                header = [str(sheet.cell(0, col).value).split('.')[0] for col in range(sheet.ncols)]
                sheet_data = []
                for row in range(1,sheet.nrows):
                    row_data = [sheet.cell(row, col).value for col in range(sheet.ncols)]
                    sheet_data.append(row_data)
                sheets_district[sheet_name] = {'header': header, 'data': sheet_data}
                print(sheet_data)

            # Merge the sheets for all districts
            for sheet_name, sheet_data in sheets_district.items():
                if sheet_name in sheets:
                    sheets[sheet_name]['data'].extend(sheet_data['data'])
                else:
                    sheets[sheet_name] = sheet_data
        except:
            # handle the case where no Excel file is found for the district
            logger.warning('Sheet Not Found')
            pass

    selected_sheet = request.GET.get('route')
    sheet_data = None
    if selected_sheet and selected_sheet in sheets:
        sheet_data = sheets[selected_sheet]

    select = request.GET.get('select')
    sheet_data1 = None
    if select in sheets or select == 'All':
        if select == 'All':
            # Export all sheets to Excel including headers
            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="fill_list.xls"'
            wb = xlwt.Workbook(encoding='utf-8')

            # Write each sheet to a separate Excel sheet
            for sheet_name, sheet_data in sheets.items():
                ws = wb.add_sheet(sheet_name)
                row_num = 0

                # Write data to Excel sheet
                for row in sheet_data['data']:
                    row_num += 1
                    for col_num, cell_value in enumerate(row):
                        ws.write(row_num, col_num, cell_value)

            wb.save(response)
            return response
        else:
            # Export selected sheet to Excel including headers
            sheet_data = sheets[select]
            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = f'attachment; filename="{select}.xls"'
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet(select)
            row_num = 0

            # Write data to Excel sheet
            for row in sheet_data['data']:
                row_num += 1
                for col_num, cell_value in enumerate(row):
                    ws.write(row_num, col_num, cell_value)

            wb.save(response)
            return response

    context = {
        'sheets': sheets,
        'selected_sheet': selected_sheet,
        'sheet_data': sheet_data,
    }

    return render(request, 'Fdashboard/route.html', context)


@login_required()
@user_passes_test(is_patner)
def route_summary_filled(request):
    # Get the current user's franchise and district
    franchise = Franchise.objects.get(user=request.user)
    districts = franchise.district.all()  # get all associated districts

    # Construct the path to the Excel file based on the districts
    csv_path = os.path.join(os.getcwd(), 'static', 'data')
    sheets = None  # initialize sheets to None

    for district in districts:
        # Assuming that each district's Excel file is named after the district's name
        file_name = f"{district.District}_summary.csv"
        file_path = os.path.join(csv_path, file_name)
        data = []

        with open(file_path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # skip the header row
            for row in reader:
                data.append(row)

    # Construct the path to the Excel file based on the districts
    csv_path = os.path.join(os.getcwd(), 'static', 'data')
    sheets = None  # initialize sheets to None

    for district in districts:
        # Assuming that each district's Excel file is named after the district's name
        file_name = f"{district.District}.csv"
        file_path = os.path.join(csv_path, file_name)
        data2 = []

        with open(file_path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # skip the header row
            for row in reader:
                data2.append(row)
    context = {
        'data': data,
        'data2': data2
    }

    return render(request, 'Fdashboard/route_filed.html', context)


@login_required()
@user_passes_test(is_patner)
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to maintain user session
            messages.success(request, 'Your password was successfully updated!')
            return redirect('FDashboard:dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(user=request.user)
    context = {'form': form}
    return render(request, 'change_password.html', context)


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
        urls = ['https://delta.busads.in/get_adcountv2.php', 'https://track.siliconharvest.net/get_adcountv2.php',
                'https://tvl.busads.in/get_adcountv2.php']
        for url in urls:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"Error response received with status code {response.status_code}")
                logger.error(f"Error response received with status code {response.status_code}")
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
                        obj, created = MyAds.objects.update_or_create(adname=AdName, imei=imei, date_time=day,
                                                                      bus_no=bus_no, route_no=route_no,
                                                                      route_name=route_name, defaults={'Count': count})
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

    # Fetch API data
    url1 = 'https://delta.busads.in/get_adcountv2.php'
    api_data1 = requests.get(url1, params=params).json()
    url2 = 'https://track.siliconharvest.net/get_adcountv2.php'
    api_data2 = requests.get(url2, params=params).json()
    url3 = 'https://tvl.busads.in/get_adcountv2.php'
    api_data3 = requests.get(url3, params=params).json()
    # print(api_data1, api_data2)

    # Print API responses to console
    # print(api_data)
    # print(api_data2)

    # Add the two API responses
    result = int(api_data1) + int(api_data2) + int(api_data3)

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
        logger.warning('Value error')

    url2 = 'https://delta.busads.in/get_adcountv2.php'
    response2 = requests.get(url2, params)
    try:
        data2 = response2.json()
    except ValueError:
        data2 = []
        logger.warning('Value error')

    url3 = 'https://tvl.busads.in/get_adcountv2.php'
    response2 = requests.get(url3, params)
    try:
        data3 = response2.json()
    except ValueError:
        data3 = []
        logger.warning('Value error')

    # Extract required information from data1 and data2
    result = []
    for data in [data1, data2, data3]:
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
        print(start_date, end_date, ad_name)

        param = {
            'name': ad_name,
            'from': start_date,
            'to': end_date,
        }
        # Query the MyAds model to get the required data
        urls = ['https://delta.busads.in/get_adcountv2.php', 'https://track.siliconharvest.net/get_adcountv2.php',
                'https://tvl.busads.in/get_adcountv2.php']
        for url in urls:
            response = requests.get(url, params=param)
            if response.status_code != 200:
                print(f"Error response received with status code {response.status_code}")
                logger.error(f"Error response received with status code {response.status_code}")
                continue
            try:
                data = response.json()
            except JSONDecodeError:
                print(f"Error decoding JSON: {response.text}")
                continue
            if data is None:
                print("API returned None")
                continue
            day_counts = defaultdict(int)
            for item in data:
                for key, value in item.items():
                    if key in ['imei', 'bus_no', 'route_no', 'route_name']:
                        continue
                    day = dt.datetime.strptime(key, "%d/%m/%Y").date().strftime("%d/%m/%Y")
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
