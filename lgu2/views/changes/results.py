
from typing import Optional

from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.urls import reverse

from ...api import effects as api
from ...api.responses.effects import Metadata
from .types import AFFECTING_YEARS, TYPES


def _get_page(request):
    page = request.GET.get('page', '1')
    try:
        page = int(page)
    except ValueError:
        page = 1
    return page


def _capture_query(type1=None, year1=None, number1=None, type2=None, year2=None, number2=None):
    affected_type = None if type1 == 'all' else type1
    affected_year = None if year1 == '*' else year1
    affected_year = int(affected_year) if affected_year is not None else None
    affected_number = int(number1) if number1 is not None else None
    affecting_type = None if type2 == 'all' else type2
    affecting_year = None if year2 == '*' else year2
    affecting_year = int(affecting_year) if affecting_year is not None else None
    affecting_number = int(number2) if number2 is not None else None
    return {
        'affected_type': affected_type,
        'affected_year': affected_year,
        'affected_number': affected_number,
        'affecting_type': affecting_type,
        'affecting_year': affecting_year,
        'affecting_number': affecting_number
    }


def _make_api_parameters(query, page):
    return {
        'targetType': query['affected_type'],
        'targetYear': query['affected_year'],
        'targetNumber': query['affected_number'],
        'sourceType': query['affecting_type'],
        'sourceYear': query['affecting_year'],
        'sourceNumber': query['affecting_number'],
        'page': page
    }


def _make_nav(meta: Metadata, link_prefix: str):

    page: int = meta['page']
    last_page: int = meta['totalPages']
    first_page_number_to_show = 1 if page < 10 else page - 9
    last_page_number_to_show = last_page if last_page < page + 9 else page + 9
    page_numbers = range(first_page_number_to_show, last_page_number_to_show + 1)

    def make_link(p: int):
        return link_prefix + '?page=' + str(p)

    pages = [{ 'number': num, 'link': make_link(num), 'class': 'currentPage' if num == page else 'pageLink' } for num in page_numbers]
    first_page = pages[0]
    last_page = pages[-1]
    first_page['class'] += ' firstPageLink'
    last_page['class'] += ' lastPageLink'
    prev = None
    next = None
    if page > first_page_number_to_show:
        prev = { 'number': page - 1, 'link': make_link(page - 1), 'class': 'pageLink prev' }
    if page < last_page_number_to_show:
        next = { 'number': page + 1, 'link': make_link(page + 1), 'class': 'pageLink next' }
    return {
        'all': pages,
        'first': first_page,
        'last': last_page,
        'prev': prev,
        'next': next
    }


def affected(request, type: str, year: Optional[str] = None, number: Optional[str] = None, format: Optional[str] = None):
    link_prefix = reverse('changes-affected', kwargs={key: value for key, value in locals().items() if key != 'request' and value is not None})
    query = _capture_query(type, year, number)
    return _combined(request, query, link_prefix, format)


def affecting(request, type: str, year: Optional[str] = None, number: Optional[str] = None, format: Optional[str] = None):
    link_prefix = reverse('changes-affecting', kwargs={key: value for key, value in locals().items() if key != 'request' and value is not None})
    query = _capture_query(type2=type, year2=year, number2=number)
    return _combined(request, query, link_prefix, format)


def both(request, type1=None, year1=None, number1=None, type2=None, year2=None, number2=None, format=None):
    link_prefix = reverse('changes-both', kwargs={key: value for key, value in locals().items() if key != 'request' and value is not None})
    query = _capture_query(type1, year1, number1, type2, year2, number2)
    return _combined(request, query, link_prefix, format)


def _combined(request, query, link_prefix, format):

    page = _get_page(request)

    api_params = _make_api_parameters(query, page)

    if format is not None:
        return _data(api_params, format)

    data = api.fetch(**api_params)

    meta = data['meta']
    meta['lastIndex'] = meta['startIndex'] + len(data['effects']) - 1

    nav = _make_nav(meta, link_prefix) if data['effects'] else {}

    context = {
        'query': query,
        'types': TYPES,
        'affecting_years': AFFECTING_YEARS,
        'meta': data['meta'],
        'pages': nav,
        'feed_link': link_prefix + '/data.feed',
        'effects': data['effects']
    }

    print("=======================RESULTS====================")
    print(context)

    template = loader.get_template('new_theme/research-tools/changes-result.html')
    return HttpResponse(template.render(context, request))


def _data(api_params, format: str):

    if format == 'feed':
        atom = api.fetch_atom(**api_params)
        return HttpResponse(atom, content_type='application/atom+xml')

    if format == 'json':
        page = api.fetch(**api_params)
        return JsonResponse(page)
