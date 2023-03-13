from django.shortcuts import render, redirect
from .forms import OfficeForm, OfficeUserForm
from django.contrib.auth.models import Group
from utility.models import District, Ads, MyAds
from .models import Office
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum


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
