
from django.contrib import admin
from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.index),
    path('admin/', admin.site.urls),
    path('hello', views.hello, name='hello'),
    path('ukpga', views.browse, name='browse'),
    path('ukpga/<int:year>', views.browse, name='browse-year'),
    re_path(r'^(?P<type>ukpga)/(?P<year>[0-9]{4})/(?P<number>[0-9]+)$', views.document, name='document'),
    re_path(r'^(?P<type>ukpga)/(?P<year>[0-9]{4})/(?P<number>[0-9]+)/metadata', views.metadata, name='metadata'),
]
