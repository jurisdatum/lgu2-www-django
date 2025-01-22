
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.template import loader
from django.urls import reverse

from ...api import effects as api
from .results import make_nav
from .types import AFFECTING_YEARS, TYPES



def both(request, type1=None, year1=None, number1=None, type2=None, year2=None, number2=None, format=None):

    # if type1 is None and year1 is None and number1 is None:
    #     return HttpResponseBadRequest()
    # if type2 is None and year2 is None and number2 is None:
    #     return HttpResponseBadRequest()

    link_prefix = reverse('changes-both', kwargs={key: value for key, value in locals().items() if key != 'request' and value is not None})
    # print(link_prefix)
    # link_prefix = '/'

    page = request.GET.get('page', '1')
    try:
        page = int(page)
    except ValueError:
        page = 1

    affected_type = None if type1 == 'all' else type1
    affected_year = None if year1 == '*' else year1
    affected_year = int(affected_year) if affected_year is not None else None
    affected_number = int(number1) if number1 is not None else None

    affecting_type = None if type2 == 'all' else type2
    affecting_year = None if year2 == '*' else year2
    affecting_year = int(affecting_year) if affecting_year is not None else None
    affecting_number = int(number2) if number2 is not None else None

    # if format:
    #     return magic_format(affected_type, affected_year, affected_number, affecting_type, affecting_year, affecting_number, format, page)
    if format == 'feed':
        atom = api.fetch_atom(targetType=affected_type, targetYear=affected_year, targetNumber=affected_number,
            sourceType=affecting_type, sourceYear=affecting_year, sourceNumber=affecting_number, page=page)
        return HttpResponse(atom, content_type='application/atom+xml')

    if format == 'json':
        page = api.fetch(targetType=affected_type, targetYear=affected_year, targetNumber=affected_number,
            sourceType=affecting_type, sourceYear=affecting_year, sourceNumber=affecting_number, page=page)
        return JsonResponse(page)

    data = api.fetch(targetType=affected_type, targetYear=affected_year, targetNumber=affected_number,
                     sourceType=affecting_type, sourceYear=affecting_year, sourceNumber=affecting_number,
                     page=page)
    meta = data['meta']

    meta['lastIndex'] = meta['startIndex'] + len(data['effects']) - 1

    nav = make_nav(meta, link_prefix) if data['effects'] else {}

    context = {
        'query': {
            'affected_type': affected_type,
            'affected_year': affected_year,
            'affected_number': affected_number,
            'affecting_type': affecting_type,
            'affecting_year': affecting_year,
            'affecting_number': affecting_number
        },
        'types': TYPES,
        'affecting_years': AFFECTING_YEARS,
        'meta': data['meta'],
        'pages': nav,
        'feed_link': link_prefix + '/data.feed',
        'effects': data['effects']
    }

    template = loader.get_template('changes/results.html')
    return HttpResponse(template.render(context, request))


# def magic_format(affected_type, affected_year, affected_number, affecting_type, affecting_year, affecting_number, format, page):

#     if format == 'feed':
#         atom = api.fetch_atom(targetType=affected_type, targetYear=affected_year, targetNumber=affected_number,
#                               sourceType=affecting_type, sourceYear=affecting_year, sourceNumber=affecting_number,
#                               page=page)
#         return HttpResponse(atom, content_type='application/atom+xml')

#     if format == 'json':
#         page = api.fetch(targetType=affected_type, targetYear=affected_year, targetNumber=affected_number,
#                          sourceType=affecting_type, sourceYear=affecting_year, sourceNumber=affecting_number,
#                          page=page)
#         return JsonResponse(page)
