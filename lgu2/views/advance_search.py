from django.shortcuts import render


def advance_search(request):
    return render(request, 'new_theme/advance_search/full_search.html')


def extent_search(request):
    return render(request, 'new_theme/advance_search/geographic_extent.html')


def point_in_time_search(request):
    return render(request, 'new_theme/advance_search/point_in_time.html')


def draft_search(request):
    return render(request, 'new_theme/advance_search/draft.html')


def impact_search(request):
    return render(request, 'new_theme/advance_search/impact.html')