from typing import Optional, Tuple
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.urls import reverse
from urllib.parse import urlencode

from ...api import effects as api
from ...api.responses.effects import Metadata
from .summary import build_changes_summary
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


def _parse_year(year: Optional[str]) -> Tuple[Optional[int], Optional[int], Optional[int]]:
    """
    Accepts:
      - '1998'
      - '1996-1998'
      - '1996-*'
      - '*-1998'
      - '*'
    Returns:
      (year, start_year, end_year)
    """

    if not year or year == '*':
        return None, None, None

    if '-' in year:
        start, end = year.split('-', 1)

        start_year = int(start) if start != '*' else None
        end_year = int(end) if end != '*' else None

        return None, start_year, end_year

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


def _localize_path(path, request):
    """Prepend the active locale prefix to a bare API path."""
    prefix = '/cy' if request.LANGUAGE_CODE == 'cy' else ''
    return f'{prefix}/{path}'


def _add_effect_links(effects, request):
    """Add locale-aware link fields to effect targets, sources, and provisions."""
    for effect in effects:
        for side in (effect['target'], effect['source']):
            side['link'] = _localize_path(side['id'], request)
            for node in side['provisions']['rich']:
                if node.get('href'):
                    node['link'] = _localize_path(node['href'], request)


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

    year = query.get(f'{prefix}_year')
    start = query.get(f'{prefix}_start_year')
    end = query.get(f'{prefix}_end_year')

    if start and end:
        params[start_key] = start
        params[end_key] = end
    elif start:
        params[start_key] = start
    elif end:
        params[end_key] = end
    elif year:
        params[year_key] = year


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
    page = meta['page']

    last_page = meta.get('totalPages', 1)

    def make_link(p):
        params = {'page': p}
        if extra_params:
            params.update(extra_params)
        return link_prefix + '?' + urlencode(params)

    pages = [
        {
            'number': p,
            'link': make_link(p),
            'class': 'currentPage' if p == page else 'pageLink'
        }
        for p in range(
            1 if page < 10 else page - 9,
            min(last_page, page + 9) + 1
        )
    ]

    return {
        'all': pages,

        'first': {'number': 1, 'link': make_link(1)} if page > 1 else None,
        'prev': {'number': page - 1, 'link': make_link(page - 1)} if page > 1 else None,
        'next': {'number': page + 1, 'link': make_link(page + 1)} if page < last_page else None,
        'last': {'number': last_page, 'link': make_link(last_page)} if page < last_page else None,
    }


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
    has_side_filters = type1 or year1 or number1 or type2 or year2 or number2
    if has_side_filters:
        viewname = 'changes-both-applied' if applied else 'changes-both'
        link_prefix = _build_link_prefix(
            viewname, applied=applied,
            type1=type1, year1=year1, number1=number1,
            type2=type2, year2=year2, number2=number2,
            format=format
        )
    else:
        link_prefix = reverse('changes-applied-only', kwargs={'applied': applied})
    query = _capture_query(type1, year1, number1, type2, year2, number2)
    return _combined(request, query, link_prefix, format, applied)


def _combined(request, query, link_prefix, format, applied):
    page = _get_page(request)
    api_params = _make_api_parameters(query, page, _get_query_titles(request), applied)

    if format:
        return _data(api_params, format)

    data = api.fetch(**api_params)
    extra_query_param = _get_extra_query_params(request, applied)
    nav = _make_nav(data['meta'], link_prefix, extra_query_param)

    # Build form values dynamically
    form_values = {
        **{
            f'{side}_{attr}': (
                query.get(f'{side}_{attr}') 
                or ('all' if attr == 'type' else '')
            )
            for side in ['affected', 'affecting']
            for attr in ['type', 'year', 'start_year', 'end_year', 'number']
        },
        'affected_title': request.GET.get('affected-title', ''),
        'affecting_title': request.GET.get('affecting-title', ''),
        'applied': applied
    }

    summary = build_changes_summary(form_values, TYPES)
    query_string = urlencode(extra_query_param)

    _add_effect_links(data['effects'], request)
    feed_url = f"{link_prefix}/data.feed?{query_string}"
    context = {
        'query': query,
        'types': TYPES,
        'affecting_years': AFFECTING_YEARS,
        'meta': data['meta'],
        'pages': nav,
        'feed_link': feed_url,
        'effects': data['effects'],
        'form_values': form_values,
        'summary': summary,
        'breadcrumbs': [
            {'text': 'Home', 'link': reverse('homepage')},
            {'text': 'Research tools', 'link': reverse('research-tools')},
            {'text': 'Changes to legislation', 'link': reverse('changes-intro')},
            {'text': 'Changes to legislation results'},
        ],
    }

    return HttpResponse(loader.get_template('new_theme/research-tools/changes-result.html').render(context, request))


def _data(api_params, format):
    if format == 'feed':
        return HttpResponse(api.fetch_atom(**api_params), content_type='application/atom+xml')
    return JsonResponse(api.fetch(**api_params))
