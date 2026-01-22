from typing import Optional
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.urls import reverse
from urllib.parse import urlencode

from ...api import effects as api
from ...api.responses.effects import Metadata
from .types import AFFECTING_YEARS, TYPES


# -------------------------
# Helpers
# -------------------------

def _get_page(request):
    """Get current page number from request GET"""
    try:
        return int(request.GET.get('page', '1'))
    except ValueError:
        return 1


def _parse_year(year: Optional[str]):
    """
    Accepts:
      - '1998'
      - '1996-1998'
      - '*'
    Returns:
      (year, start_year, end_year)
    """
    if not year or year == '*':
        return None, None, None
    if '-' in year:
        start, end = year.split('-', 1)
        return None, int(start), int(end)
    return int(year), None, None


def _get_query_titles(request):
    """Return title params for API call"""
    return {k: v for k, v in {
        'targetTitle': request.GET.get('affected-title'),
        'sourceTitle': request.GET.get('affecting-title')
    }.items() if v}


def _get_extra_query_params(request, applied=None):
    """Extra query params for pagination links"""
    query = {}
    if applied in ('applied', 'unapplied'):
        query['applied'] = applied
    for k in ['affected-title', 'affecting-title']:
        if request.GET.get(k):
            query[k] = request.GET[k]
    return query


def _capture_side(type_, year, number):
    """Capture one side of query"""
    t = None if type_ == 'all' else type_
    y, start, end = _parse_year(year)
    n = int(number) if number else None
    return t, y, start, end, n


def _capture_query(type1=None, year1=None, number1=None,
                   type2=None, year2=None, number2=None):
    a = _capture_side(type1, year1, number1)
    b = _capture_side(type2, year2, number2)
    keys = ['type', 'year', 'start_year', 'end_year', 'number']
    return {
        **{f'affected_{k}': v for k, v in zip(keys, a)},
        **{f'affecting_{k}': v for k, v in zip(keys, b)},
    }


def _add_year_params(params, query, prefix, year_key, start_key, end_key):
    """
    Add year params to API request, using exact keys expected by API
    """
    if query[f'{prefix}_start_year'] and query[f'{prefix}_end_year']:
        params[start_key] = query[f'{prefix}_start_year']
        params[end_key] = query[f'{prefix}_end_year']
    else:
        params[year_key] = query[f'{prefix}_year']


def _make_api_parameters(query, page, title_params=None, applied=None):
    params = {
        'targetType': query['affected_type'],
        'targetNumber': query['affected_number'],
        'sourceType': query['affecting_type'],
        'sourceNumber': query['affecting_number'],
        'page': page,
    }

    _add_year_params(params, query, 'affected', 'targetYear', 'targetStartYear', 'targetEndYear')
    _add_year_params(params, query, 'affecting', 'sourceYear', 'sourceStartYear', 'sourceEndYear')

    if applied in ('applied', 'unapplied'):
        params['applied'] = applied

    if title_params:
        params.update(title_params)

    # Remove None values
    return {k: v for k, v in params.items() if v is not None}


def _make_nav(meta: Metadata, link_prefix: str, extra_params=None):
    page, last_page = meta['page'], meta['totalPages']
    first, last = (1 if page < 10 else page - 9), min(last_page, page + 9)

    def make_link(p):
        params = {'page': p}
        if extra_params:
            params.update(extra_params)
        return link_prefix + '?' + urlencode(params)

    pages = [{'number': p, 'link': make_link(p), 'class': 'currentPage' if p == page else 'pageLink'}
             for p in range(first, last + 1)]

    return {'all': pages,
            'prev': make_link(page - 1) if page > first else None,
            'next': make_link(page + 1) if page < last else None}


# -------------------------
# Views
# -------------------------

def _build_link_prefix(viewname, **kwargs):
    """Reverse URL and remove None kwargs"""
    return reverse(viewname, kwargs={k: v for k, v in kwargs.items() if v is not None})


def affected(request, applied=None, type=None, year=None, number=None, format=None):
    viewname = 'changes-affected-applied' if applied else 'changes-affected'
    link_prefix = _build_link_prefix(viewname, applied=applied, type=type, year=year, number=number, format=format)
    query = _capture_query(type1=type, year1=year, number1=number)
    return _combined(request, query, link_prefix, format, applied)


def affecting(request, applied=None, type=None, year=None, number=None, format=None):
    viewname = 'changes-affecting-applied' if applied else 'changes-affecting'
    link_prefix = _build_link_prefix(viewname, applied=applied, type=type, year=year, number=number, format=format)
    query = _capture_query(type2=type, year2=year, number2=number)
    return _combined(request, query, link_prefix, format, applied)


def both(request, applied=None, type1=None, year1=None, number1=None,
         type2=None, year2=None, number2=None, format=None):
    viewname = 'changes-both-applied' if applied else 'changes-both'
    link_prefix = _build_link_prefix(
        viewname, applied=applied,
        type1=type1, year1=year1, number1=number1,
        type2=type2, year2=year2, number2=number2,
        format=format
    )
    query = _capture_query(type1, year1, number1, type2, year2, number2)
    return _combined(request, query, link_prefix, format, applied)


def _combined(request, query, link_prefix, format, applied):
    page = _get_page(request)
    api_params = _make_api_parameters(query, page, _get_query_titles(request), applied)

    if format:
        return _data(api_params, format)

    data = api.fetch(**api_params)
    nav = _make_nav(data['meta'], link_prefix, _get_extra_query_params(request, applied))

    # Build form values dynamically
    form_values = {**{f'{side}_{attr}': query[f'{side}_{attr}'] or ('all' if attr == 'type' else None)
                      for side in ['affected', 'affecting'] for attr in ['type','year','start_year','end_year','number']},
                   'affected_title': request.GET.get('affected-title',''),
                   'affecting_title': request.GET.get('affecting-title',''),
                   'applied': applied}

    context = {
        'query': query,
        'types': TYPES,
        'affecting_years': AFFECTING_YEARS,
        'meta': data['meta'],
        'pages': nav,
        'feed_link': link_prefix + '/data.feed',
        'effects': data['effects'],
        'form_values': form_values,
    }

    return HttpResponse(loader.get_template('new_theme/research-tools/changes-result.html').render(context, request))


def _data(api_params, format):
    if format == 'feed':
        return HttpResponse(api.fetch_atom(**api_params), content_type='application/atom+xml')
    return JsonResponse(api.fetch(**api_params))
