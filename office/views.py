from django.shortcuts import render, redirect
from .forms import OfficeForm, OfficeUserForm
from django.contrib.auth.models import Group

from .models import Office


# Create your views here.
def dashboard(request):
    return render(request, 'office/dashboard.html')


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
