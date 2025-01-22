
from typing import Optional

from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.urls import reverse

from ...api import effects as api
from ...api.responses.effects import Metadata
from .types import AFFECTING_YEARS, TYPES


def make_nav(meta: Metadata, link_prefix: str):

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


def affected(request, type: str, year: Optional[str] = None, number: Optional[str] = None):

    page = request.GET.get('page', '1')
    try:
        page = int(page)
    except ValueError:
        page = 1

    # convert parameters for API call
    type2 = None if type == 'all' else type
    year2 = int(year) if year is not None else None
    number2 = int(number) if number is not None else None

    data = api.fetch(targetType=type2, targetYear=year2, targetNumber=number2, page=page)
    meta = data['meta']

    meta['lastIndex'] = meta['startIndex'] + len(data['effects']) - 1

    if year is None:
        if number is None:
            link_prefix = reverse('changes-affected-type', kwargs={'type': type})
        else:
            link_prefix = reverse('changes-affected-type-number', kwargs={'type': type, 'number': number})
    else:
        if number is None:
            link_prefix = reverse('changes-affected-type-year', kwargs={'type': type, 'year': year})
        else:
            link_prefix = reverse('changes-affected-type-year-number', kwargs={'type': type, 'year': year, 'number': number})

    nav = make_nav(meta, link_prefix) if data['effects'] else {}

    context = {
        'query': {
            'affected_type': type,
            'affected_year': year,
            'affected_number': number
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


def affecting(request, type: str, year: Optional[str] = None, number: Optional[str] = None):

    page = request.GET.get('page', '1')
    try:
        page = int(page)
    except ValueError:
        page = 1

    # convert parameters for API call
    type2 = None if type == 'all' else type
    year2 = int(year) if year is not None else None
    number2 = int(number) if number is not None else None

    data = api.fetch(sourceType=type2, sourceYear=year2, sourceNumber=number2, page=page)
    meta = data['meta']

    meta['lastIndex'] = meta['startIndex'] + len(data['effects']) - 1

    if year is None:
        if number is None:
            link_prefix = reverse('changes-affecting-type', kwargs={'type': type})
        else:
            link_prefix = reverse('changes-affecting-type-number', kwargs={'type': type, 'number': number})
    else:
        if number is None:
            link_prefix = reverse('changes-affecting-type-year', kwargs={'type': type, 'year': year})
        else:
            link_prefix = reverse('changes-affecting-type-year-number', kwargs={'type': type, 'year': year, 'number': number})

    nav = make_nav(meta, link_prefix) if data['effects'] else {}

    context = {
        'query': {
            'affecting_type': type,
            'affecting_year': year2,
            'affecting_number': number
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

# data

def affected_data(request, format: str, type: str, year: Optional[str] = None, number: Optional[str] = None):

    page = request.GET.get('page', '1')
    try:
        page = int(page)
    except ValueError:
        page = 1

    # convert parameters for API call
    type2 = None if type == 'all' else type
    year2 = int(year) if year is not None else None
    number2 = int(number) if number is not None else None

    if format == 'feed':
        atom = api.fetch_atom(targetType=type2, targetYear=year2, targetNumber=number2, page=page)
        return HttpResponse(atom, content_type='application/atom+xml')

    if format == 'json':
        page = api.fetch(targetType=type2, targetYear=year2, targetNumber=number2, page=page)
        return JsonResponse(page)

    return HttpResponse(status=406)


def affecting_data(request, format: str, type: str, year: Optional[str] = None, number: Optional[str] = None):

    page = request.GET.get('page', '1')
    try:
        page = int(page)
    except ValueError:
        page = 1

    # convert parameters for API calls
    type2 = None if type == 'all' else type
    year2 = int(year) if year is not None else None
    number2 = int(number) if number is not None else None

    if format == 'feed':
        atom = api.fetch_atom(sourceType=type2, sourceYear=year2, sourceNumber=number2, page=page)
        return HttpResponse(atom, content_type='application/atom+xml')

    if format == 'json':
        page = api.fetch(sourceType=type2, sourceYear=year2, sourceNumber=number2, page=page)
        return JsonResponse(page)

    return HttpResponse(status=406)
