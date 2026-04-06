
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse

from .redirect import get_redirect
from .summary import build_changes_summary
from .types import AFFECTING_YEARS, TYPES

# Empty form values for the intro page (no search yet)
_EMPTY_FORM_VALUES = {
    f'{side}_{attr}': ''
    for side in ['affected', 'affecting']
    for attr in ['type', 'year', 'start_year', 'end_year', 'number', 'title']
}


def intro(request):

    redrct = get_redirect(request)
    if redrct:
        return redrct

    summary = build_changes_summary(_EMPTY_FORM_VALUES, TYPES)
    context = {
        'types': TYPES,
        'affecting_years': AFFECTING_YEARS,
        'summary': summary,
        'breadcrumbs': [
            {'text': 'Home', 'link': reverse('homepage')},
            {'text': 'Research tools', 'link': reverse('research-tools')},
            {'text': 'Changes to legislation'},
        ],
    }
    template = loader.get_template('new_theme/research-tools/changes.html')
    return HttpResponse(template.render(context, request))
