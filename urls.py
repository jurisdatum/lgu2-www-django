
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
    re_path(r'^(?P<type>ukpga)/(?P<year>[0-9]{4})/(?P<number>[0-9]+)/data.xml$', views.document_clml),
    re_path(r'^(?P<type>ukpga)/(?P<year>[0-9]{4})/(?P<number>[0-9]+)/data.akn$', views.document_akn),

    re_path(r'^(?P<type>ukpga)/(?P<year>[0-9]{4})/(?P<number>[0-9]+)/(?P<version>enacted|\d{4}-\d{2}-\d{2})$', views.document, name='document-version'),
    re_path(r'^(?P<type>ukpga)/(?P<year>[0-9]{4})/(?P<number>[0-9]+)/(?P<version>enacted|\d{4}-\d{2}-\d{2})/data.xml$', views.document_clml),
    re_path(r'^(?P<type>ukpga)/(?P<year>[0-9]{4})/(?P<number>[0-9]+)/(?P<version>enacted|\d{4}-\d{2}-\d{2})/data.akn$', views.document_akn),

    re_path(r'^(?P<type>ukpga)/(?P<year>[0-9]{4})/(?P<number>[0-9]+)/metadata', views.metadata, name='metadata'),
    re_path(r'^(?P<type>ukpga)/(?P<year>[0-9]{4})/(?P<number>[0-9]+)/combined', views.combined),

]
