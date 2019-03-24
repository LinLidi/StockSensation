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
from StockVisualData import views as StockVisualData_views
from Stockline import views as Kline_views
from stock_dic_opinion import views as opinion_views




urlpatterns = [
       path('admin/', admin.site.urls),
       path('home/',Kline_views.home),
       path('pyecharts/',opinion_views.index),
       url(r'^$', StockVisualData_views.home, name='home'),
       url(r'^index/$', StockVisualData_views.index, name='index'),
       url(r'^stockKLine/$', StockVisualData_views.stockKLine, name='stockKline'),
       
       url(r'^wordcloud/$', StockVisualData_views.wordcloud, name='wordcloud'),
       url(r'^wordcloudResult/$', StockVisualData_views.wordcloudResult, name='wordcloudResult'),
       
       url(r'^dicopinion/$', StockVisualData_views.dicopinion, name='dicopinion'),
       url(r'^dicopinionResult/$', StockVisualData_views.dicopinionResult, name='dicopinionResult'),
       
       url(r'^nbopinion/$', StockVisualData_views.nbopinion, name='nbopinion'),
       url(r'^nbopinionResult/$', StockVisualData_views.nbopinionResult, name='nbopinionResult'),
       
       ]
