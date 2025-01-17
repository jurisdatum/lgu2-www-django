
from typing import Optional

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse

from lgu2.api.responses.effects2 import Metadata

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
        'meta': data['meta'],
        'pages': nav,
        'feed_link': link_prefix + '/data.feed',
        'effects': data['effects']
    }

    template = loader.get_template('changes/results.html')
    return HttpResponse(template.render(context, request))


def affected_data(request, format: str, type: str, year: Optional[str] = None, number: Optional[str] = None):

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
        atom = api.fetch_atom(targetType=type2, targetYear=year2, targetNumber=number2, page=page)
        return HttpResponse(atom, content_type='application/atom+xml')

    if format == 'json':
        page = api.fetch(targetType=type2, targetYear=year2, targetNumber=number2, page=page)
        return JsonResponse(page)

    return HttpResponse(status=406)
