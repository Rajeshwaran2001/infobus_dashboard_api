from django.shortcuts import render, redirect, reverse

# Create your views here.


def is_patner(user):
    return user.groups.filter(name='Franchise').exists()


def is_office(user):
    return user.groups.filter(name='Office').exists()


def afterlogin_view(request):
    if is_patner(request.user):
        return redirect('FDashboard:dashboard')

    elif is_office(request.user):
        return render(request, 'FDashboard:dashboard')
    else:
        return redirect('FDashboard:Flogin')
