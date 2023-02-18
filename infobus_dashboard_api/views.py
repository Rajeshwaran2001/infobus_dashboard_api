from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum
from api.ads.models import Ads
from dashboard.models import MyAds
from utility.models import bus_Detail


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
        # print(myad)
        # print(bus_nos)

        if ad.myads_count is not None:  # To handle the total count is 0
            if ad.TotalCount:
                # print(ad.AdName, ad.myads_count, ad.TotalCount)
                ad.percentage = (ad.myads_count / ad.TotalCount) * 100
            else:
                ad.percentage = 0
        else:
            ad.percentage = 0

        mylist = zip(myad, bus_nos)
        return render(request, 'customer/detail.html', {'ad': ad, 'mylist': mylist})

    # If request method is not POST, render the form
    return render(request, 'customer/login.html')


