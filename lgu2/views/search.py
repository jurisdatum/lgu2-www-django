from django.shortcuts import render
from urllib.parse import urlencode
from ..api.search import basic_search
from collections import defaultdict
from ..util.cutoff import get_cutoff
import string

def search_results(request):
    # Get query parameters from the URL
    api_data, query_params = basic_search(request)
    
    total_count_by_type = sum(item['count'] for item in api_data['meta']['counts']['byType'])
    total_count_by_year = sum(item['count'] for item in api_data['meta']['counts']['byYear'])

    # Calculate page range
    total_pages = api_data['meta']['totalPages']
    current_page = api_data['meta']['page']

    if total_pages <= 10:
        page_range = range(1, total_pages + 1)
    else:
        start = max(1, current_page - 5)
        end = min(total_pages, start + 9)
        page_range = range(start, end + 1)

    modified_query_links = {}
    for key in request.GET.dict():
        new_query = query_params.copy()
        new_query.pop(key, None)
        modified_query_links[key] = urlencode(new_query)
    
    query_dict = request.GET.copy()
    query_dict.pop('page', None)  # Remove any existing 'page' param
    base_query = urlencode(query_dict)

    by_year_pagination_count = len(api_data['meta']['counts']['byYear'])
    current_year = str(query_params.get("year"))
    current_type = query_params.get("type")
    
    grouped_by_decade = False
    if len(api_data['meta']['counts']['byType']) == 1:
        grouped_by_decade = group_by_decade(api_data['meta']['counts']['byYear'], current_type)

    subject_initials = None
    if 'bySubjectInitial' in api_data['meta']['counts']:  # should not be present and None
        subject_initials = set([i['initial'] for i in api_data['meta']['counts']['bySubjectInitial']])

    context = {
        "meta_data": api_data["meta"],
        "documents_data": api_data["documents"],
        "page_range": page_range,
        "current_page": current_page,
        "total_pages": total_pages,
        "total_count_by_type":total_count_by_type,
        "total_count_by_year":total_count_by_year,
        "modified_query_links": modified_query_links,
        'query_params': f'?{base_query}' if base_query else '',
        "by_year_pagination_count": by_year_pagination_count,
        "current_year": current_year,
        "current_type": current_type,
        "grouped_by_decade": grouped_by_decade,
        "subject_initials": subject_initials,
        'all_lowercase_letters': string.ascii_lowercase,
    }

    return render(request, 'new_theme/search_result/search_result.html', context)




def group_by_decade(year_data, doc_type):
    cut_off = get_cutoff(doc_type)
    grouped = defaultdict(dict)

    # Fill available years
    for entry in year_data:
        year = entry["year"]
        count = entry["count"]
        complete = year > cut_off
        decade_start = (year // 10) * 10
        decade_label = f"{decade_start}-{decade_start + 9}"
        grouped[decade_label][year] = {
            "year": year,
            "count": count,
            "complete": complete
        }

    # Add missing years with "No data"
    filled_grouped = {}
    for decade_label, years_dict in grouped.items():
        decade_start = int(decade_label.split("-")[0])
        full_years = []
        for y in range(decade_start, decade_start + 10):
            if y in years_dict:
                full_years.append(years_dict[y])
            else:
                full_years.append({
                    "year": y,
                    "count": 0,
                    "complete": False,
                    "no_data": True  # extra flag for template
                })
        filled_grouped[decade_label] = full_years

    # Sort decades descending
    return dict(sorted(filled_grouped.items(), reverse=False))