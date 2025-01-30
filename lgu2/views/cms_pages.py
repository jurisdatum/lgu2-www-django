from django.http import HttpResponse
from django.template import loader
from ..models import *

def about_us(request):
    footer_data = Footer.objects.all().first()
    about_us_data = AboutUsPage.objects.all().first()
    about_us_sub_sec = AboutUsPageSubSection.objects.all()

    data = {}
    data['footer'] = footer_data
    data['about_us_data'] = about_us_data
    data['about_us_sub_sec'] = about_us_sub_sec
    template = loader.get_template('browse/about_us.html')
    return HttpResponse(template.render(data, request))
