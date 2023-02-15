"""infobus_dashboard_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from infobus_dashboard_api import views
from django.conf.urls.static import static
from django.conf import settings

app_name = "home"

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('api/', include('api.urls')),
                  path('dashboard/', include('dashboard.urls')),
                  path('utlity/', include('utility.urls')),
                  path('afterlogin', views.afterlogin_view, name='afterlogin'),
                  path('login/', views.login_user, name='Login'),
                  path('logout/', views.logout_user, name='Logout'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
