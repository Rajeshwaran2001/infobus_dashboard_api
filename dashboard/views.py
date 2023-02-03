from django.shortcuts import render, redirect
from api.ads.models import Ads
from dashboard.forms import ServiceUserForm
from django.contrib.auth.models import Group

# Create your views here.


def listads(request):
    ads = Ads.objects.all()

    return render(request, 'Fdashboard/dashboard.html', {'ads': ads})


def service_engineer_signup_view(request):
    userForm = ServiceUserForm()
    mydict = {'userForm': userForm}
    if request.method == 'POST':
        userForm = ServiceUserForm(request.POST)
        if userForm.is_valid() :
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            my_group = Group.objects.get_or_create(name='Franchise')
            my_group[0].user_set.add(user)
        return redirect('FDashboard:Flogin')
    return render(request, 'Fdashboard/signup.html', context=mydict)
