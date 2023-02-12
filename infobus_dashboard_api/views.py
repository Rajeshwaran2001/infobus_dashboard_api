from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
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
