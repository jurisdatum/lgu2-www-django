
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse

from .redirect import get_redirect
from .types import AFFECTING_YEARS, TYPES


def intro(request):

    redrct = get_redirect(request)
    if redrct:
        return redrct

    context = {
        'types': TYPES,
        'affecting_years': AFFECTING_YEARS,
        'breadcrumbs': [
            {'text': 'Home', 'link': reverse('homepage')},
            {'text': 'Research tools', 'link': reverse('research-tools')},
            {'text': 'Changes to legislation'},
        ],
    }
    template = loader.get_template('new_theme/research-tools/changes.html')
    return HttpResponse(template.render(context, request))
