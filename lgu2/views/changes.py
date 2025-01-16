
from typing import Optional

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template import loader

from ..api import effects as api


TYPES = {
    'ukpga': "UK Public General Acts",
    'ukla': "UK Local Acts",
    'apgb': "Acts of the Parliament of Great Britain",
    'aep': "Acts of the English Parliament",
    'aosp': "Acts of the Old Scottish Parliament",
    'asp': "Acts of the Scottish Parliament",
    'aip': "Acts of the Old Irish Parliament",
    'apni': "Acts of the Northern Ireland Parliament",
    'mnia': "Measures of the Northern Ireland Assembly",
    'nia': "Acts of the Northern Ireland Assembly",
    'ukcm': "Church Measures",
    'asc': "Acts of Senedd Cymru",
    'anaw': "Acts of the National Assembly for Wales",
    'mwa': "Measures of the National Assembly for Wales",
    'uksi': "UK Statutory Instruments",
    'ssi': "Scottish Statutory Instruments",
    'wsi': "Wales Statutory Instruments",
    'nisr': "Northern Ireland Statutory Rules",
    'nisi': "Northern Ireland Orders in Council",
    'nisro': "Northern Ireland Statutory Rules and Orders",
    'eur': "Regulations originating from the EU",
    'eudn': "Decisions originating from the EU",
    'eudr': "Directives originating from the EU",
}


def intro(request):

    affected_type = request.GET.get('affected-type')
    affected_year = request.GET.get('affected-year')
    affected_number = request.GET.get('affected-number')
    if affected_type:
        if affected_year:
            if affected_number:
                return redirect('changes-affected-type-year-number', type=affected_type, year=affected_year, number=affected_number)
            else:
                return redirect('changes-affected-type-year', type=affected_type, year=affected_year)
        else:
            if affected_number:
                return redirect('changes-affected-type-number', type=affected_type, number=affected_number)
            else:
                return redirect('changes-affected-type', type=affected_type)
    if request.GET:
        # log unrecognized parameters
        return redirect('changes-intro')

    context = {
        'types': TYPES
    }

    template = loader.get_template('changes/intro.html')
    return HttpResponse(template.render(context, request))


def affected(request, type: str, year: Optional[str] = None, number: Optional[str] = None):

    if type == 'all':
        type = None

    page = api.fetch(targetType=type, targetYear=year, targetNumber=number)

    context = {
        'query': {
            'affected_type': type,
            'affected_year': year,
            'affected_number': number
        },
        'types': TYPES,
        'meta': page['meta'],
        'effects': page['effects']
    }

    template = loader.get_template('changes/results.html')
    return HttpResponse(template.render(context, request))
