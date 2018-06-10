from django.conf.urls import url
from . import views

app_name = 'stockdata'
urlpatterns = [
   url(r'^pyechart3d/$', views.pyechart3d, name='pyechart3d'),
   url(r'^etest/$', views.etest, name='etest'),
   url(r'^new/$', views.new, name='new'),
]