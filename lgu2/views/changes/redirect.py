from django.http import HttpResponseRedirect
from django.urls import reverse
from urllib.parse import urlencode


# -------------------------
# Helpers
# -------------------------

def _extract_year_range(prefix, request):
    """
    Returns:
    - 'YYYY-YYYY' if a range is selected
    - 'YYYY' if a single year is selected
    - None if nothing selected
    """
    start = request.GET.get(f'{prefix}-start-year')
    end = request.GET.get(f'{prefix}-end-year')

    if start and end:
        return f'{start}-{end}'

    return request.GET.get(f'{prefix}-year')


def _title_query_args(request):
    """Titles are the only allowed query string parameters"""
    return {k: v for k, v in {
        'affected-title': request.GET.get('affected-title'),
        'affecting-title': request.GET.get('affecting-title')
    }.items() if v}


def redirect_with_query(viewname, path_kwargs=None, query_kwargs=None):
    """Reverse URL and attach query params"""
    path_kwargs = path_kwargs or {}
    query_kwargs = query_kwargs or {}

    url = reverse(viewname, kwargs=path_kwargs)
    if query_kwargs:
        url += '?' + urlencode(query_kwargs)
    return HttpResponseRedirect(url)


def _get_viewname(base, applied):
    """Return correct view name depending on applied/unapplied"""
    if applied in ('applied', 'unapplied'):
        return f'{base}-applied'
    return base


def _normalize_value(value, default='all', allow_star_if_number=False):
    """Helper to normalize type/year/number for redirect"""
    if value is None and allow_star_if_number:
        return '*'  # for year if number exists but year is missing
    return value or default


def _redirect_generic(base, types, years, numbers, applied, request):
    """
    Generic redirect function for affected, affecting, or both
    `types`, `years`, `numbers` are dicts with keys matching URL kwargs
    """
    path_args = {}
    for k, v in types.items():
        path_args[k] = _normalize_value(v, default='all', allow_star_if_number=False)
    for k, v in numbers.items():
        path_args[k] = v or None
    for k, v in years.items():
        # Use '*' if number exists but year is missing
        path_args[k] = _normalize_value(v, default=None, allow_star_if_number=path_args.get(k.replace('year', 'number')) is not None)

    # Remove None values
    path_args = {k: v for k, v in path_args.items() if v is not None}

    if applied in ('applied', 'unapplied'):
        path_args['applied'] = applied

    return redirect_with_query(_get_viewname(base, applied), path_args, _title_query_args(request))


# -------------------------
# Main redirect logic
# -------------------------

def get_redirect(request):
    applied = request.GET.get('applied')

    # Gather affected params
    affected_type = request.GET.get('affected-type')
    affected_year = _extract_year_range('affected', request)
    affected_number = request.GET.get('affected-number')

    # Gather affecting params
    affecting_type = request.GET.get('affecting-type')
    affecting_year = _extract_year_range('affecting', request)
    affecting_number = request.GET.get('affecting-number')

    has_affected = affected_type or affected_year or affected_number
    has_affecting = affecting_type or affecting_year or affecting_number

    if has_affected and has_affecting:
        return _redirect_generic(
            'changes-both',
            types={'type1': affected_type, 'type2': affecting_type},
            years={'year1': affected_year, 'year2': affecting_year},
            numbers={'number1': affected_number, 'number2': affecting_number},
            applied=applied,
            request=request
        )

    if has_affected:
        return _redirect_generic(
            'changes-affected',
            types={'type': affected_type},
            years={'year': affected_year},
            numbers={'number': affected_number},
            applied=applied,
            request=request
        )

    if has_affecting:
        return _redirect_generic(
            'changes-affecting',
            types={'type': affecting_type},
            years={'year': affecting_year},
            numbers={'number': affecting_number},
            applied=applied,
            request=request
        )
