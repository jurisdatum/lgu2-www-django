
from django.shortcuts import redirect


def get_redirect(request):

    affected_type = request.GET.get('affected-type')
    affected_year = request.GET.get('affected-year')
    affected_number = request.GET.get('affected-number')

    affecting_type = request.GET.get('affecting-type')
    affecting_year = request.GET.get('affecting-year')
    affecting_number = request.GET.get('affecting-number')

    if affected_type or affected_year or affected_number:
        if affecting_type or affecting_year or affecting_number:
            return _get_redirect_both(affected_type, affected_year, affected_number, affecting_type, affecting_year, affecting_number)
        else:
            return _get_redirect_affected(affected_type, affected_year, affected_number)
    else:
        if affecting_type or affecting_year or affecting_number:
            return _get_redirect_affecting(affecting_type, affecting_year, affecting_number)
        else:
            pass


def _get_redirect_affected(affected_type, affected_year, affected_number):

    if not affected_type:
        affected_type = 'all'
    if not affected_year:
        affected_year = None
    if not affected_number:
        affected_number = None
    if affected_year is None and affected_number is not None:
        affected_year = '*'

    args = {
        'type': affected_type,
        'year': affected_year,
        'number': affected_number
    }
    args = {key: value for key, value in args.items() if value is not None}
    return redirect('changes-affected', **args)


def _get_redirect_affecting(affecting_type, affecting_year, affecting_number):

    if not affecting_type:
        affecting_type = 'all'
    if not affecting_year:
        affecting_year = None
    if not affecting_number:
        affecting_number = None
    if affecting_year is None and affecting_number is not None:
        affecting_year = '*'

    args = {
        'type': affecting_type,
        'year': affecting_year,
        'number': affecting_number
    }
    args = {key: value for key, value in args.items() if value is not None}
    return redirect('changes-affecting', **args)


def _get_redirect_both(affected_type, affected_year, affected_number, affecting_type, affecting_year, affecting_number):

    if not affected_type:
        affected_type = 'all'
    if not affected_year:
        affected_year = None
    if not affected_number:
        affected_number = None
    if affected_year is None and affected_number is not None:
        affected_year = '*'

    if not affecting_type:
        affecting_type = 'all'
    if not affecting_year:
        affecting_year = None
    if not affecting_number:
        affecting_number = None
    if affecting_year is None and affecting_number is not None:
        affecting_year = '*'

    args = {
        'type1': affected_type,
        'year1': affected_year,
        'number1': affected_number,
        'type2': affecting_type,
        'year2': affecting_year,
        'number2': affecting_number
    }
    args = {key: value for key, value in args.items() if value is not None}
    return redirect('changes-both', **args)
