from django.http import HttpResponse
from django.template import loader

def explore_collection(request):
    template = loader.get_template('collection/explore.html')
    return HttpResponse(template.render())


def explore_legislatures(request):
    template = loader.get_template('collection/legislatures.html')
    return HttpResponse(template.render())