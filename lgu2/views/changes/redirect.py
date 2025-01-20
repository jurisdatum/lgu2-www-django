
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
            return _get_redirect_affected(affected_type, affected_year, affected_number)  # FixMe
        else:
            return _get_redirect_affected(affected_type, affected_year, affected_number)
    else:
        if affecting_type or affecting_year or affecting_number:
            return _get_redirect_affecting(affecting_type, affecting_year, affecting_number)
        else:
            pass


def _get_redirect_affected(affected_type, affected_year, affected_number):
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


def _get_redirect_affecting(affecting_type, affecting_year, affecting_number):
    if affecting_type:
        if affecting_year:
            if affecting_number:
                return redirect('changes-affecting-type-year-number', type=affecting_type, year=affecting_year, number=affecting_number)
            else:
                return redirect('changes-affecting-type-year', type=affecting_type, year=affecting_year)
        else:
            if affecting_number:
                return redirect('changes-affecting-type-number', type=affecting_type, number=affecting_number)
            else:
                return redirect('changes-affecting-type', type=affecting_type)
