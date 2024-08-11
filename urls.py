
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('hello', views.hello, name='hello'),
    path('ukpga', views.browse, name='ukpga'),
    path('<type>/<int:year>/<int:number>', views.document, name='document'),
]
