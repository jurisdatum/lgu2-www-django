
from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('admin/', admin.site.urls),
    path('hello', views.hello, name='hello'),
    path('ukpga', views.browse, name='browse'),
    path('ukpga/<int:year>', views.browse, name='browse-year'),
    path('<type>/<int:year>/<int:number>', views.document, name='document'),
]
