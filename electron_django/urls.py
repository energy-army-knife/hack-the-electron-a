"""electron_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.views.generic import RedirectView

from webapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    url(r'^$', views.index, name='index'),
    url(r'^analyser/$', views.analyser, name='analyser'),
    url(r'^last_bills/$', views.last_bills, name='last_bills'),
    url(r'^photovoltaic/$', views.pv, name='photovoltaic'),
    url(r'^device_simulator/$', views.device_simulator, name='device_simulator'),
    url(r'^contract_subscription/$', views.contract_subscription, name='contract_subscription'),
    url(r'^tariff_subscription/$', views.tariff_subscription, name='tariff_subscription'),
    url(r'^notifications/$', views.notifications, name='notificatons'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^favicon\.ico$', RedirectView.as_view(url='static/images/favicon.ico')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
