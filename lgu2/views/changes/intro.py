
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader

from .redirect import get_redirect
from .types import AFFECTING_YEARS, TYPES


def intro(request):

    redrct = get_redirect(request)
    if redrct:
        return redrct
    if request.GET:
        # log unrecognized parameters
        return redirect('changes-intro')

    context = { 'types': TYPES, 'affecting_years': AFFECTING_YEARS }
    template = loader.get_template('changes/intro.html')
    return HttpResponse(template.render(context, request))
