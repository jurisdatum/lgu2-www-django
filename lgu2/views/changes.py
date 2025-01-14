
from typing import Optional

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template import loader

from ..api import effects as api


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

    template = loader.get_template('changes/intro.html')
    return HttpResponse(template.render({}, request))


def affected(request, type: str, year: Optional[str] = None, number: Optional[str] = None):
    if type == 'all':
        type = None
    # effects = api.fetch(targetType=type, targetYear=year, targetNumber=number)
    template = loader.get_template('changes/results.html')
    return HttpResponse(template.render({}, request))