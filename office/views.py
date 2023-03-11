from django.shortcuts import render, redirect
from .forms import OfficeForm
from django.contrib.auth.models import Group


# Create your views here.
def dashboard(request):

    return render(request, 'office/dashboard.html')



def Office_signup_view(request):
    userForm = OfficeForm()
    mydict = {'userForm': userForm}
    if request.method == 'POST':
        userForm = OfficeForm(request.POST)
        if userForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()

            my_group = Group.objects.get_or_create(name='Office')
            my_group[0].user_set.add(user)
        return redirect('Office:Office-login')
    return render(request, 'office/signup.html', context=mydict)
