"""stock URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from stockdata import views as stockdata_views




urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$', stockdata_views.home, name='home'),
    url(r'^wordcloud/$', stockdata_views.wordcloud, name='wordcloud'),
    url(r'^dicopinion/$', stockdata_views.dicopinion, name='dicopinion'),
    url(r'^nbopinion/$', stockdata_views.nbopinion, name='nbopinion'),

    url(r'^echarts/$', stockdata_views.index, name='index'),
    url(r'^basedic/$', stockdata_views.basedicf, name='basedic'),
    url(r'^basedicgraph/$', stockdata_views.basedic, name='basedicgraph'),
    url(r'^stockKLine/$', stockdata_views.stockKLine, name='stockKline'),
]
