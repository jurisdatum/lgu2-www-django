from django.http import HttpResponse
from django.template import loader
from ..api.explore_collection import get_legislature_by_country_type

def explore_collection(request):
    template = loader.get_template('collection/explore.html')
    return HttpResponse(template.render())


def explore_legislatures(request):
    template = loader.get_template('collection/legislatures.html')
    return HttpResponse(template.render())

def legislature_list(request, type):
    doc_list = get_legislature_by_country_type(type)
    print(doc_list)
    template = loader.get_template('collection/legislature_list.html')
    return HttpResponse(template.render(doc_list, request))