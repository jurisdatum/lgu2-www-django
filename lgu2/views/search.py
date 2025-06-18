from django.shortcuts import render
import requests
from django.conf import settings

SERVER = settings.API_BASE_URL

def search_results(request):
    # Get query parameters from the URL
    query_params = request.GET.dict()
    print(query_params)
    query_params = {key: value for key, value in query_params.items() if value}
    api_url = SERVER+'/search'
    
    response = requests.get(api_url, params=query_params)
    api_data = response.json() if response.status_code == 200 else {}
    
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

    context = {
        "meta_data": api_data["meta"],
        "documents_data": api_data["documents"],
        "page_range": page_range,
        "current_page": current_page,
        "total_pages": total_pages,
        "total_count_by_type":total_count_by_type,
        "total_count_by_year":total_count_by_year
    }

    return render(request, 'new_theme/search_result/search_result.html', context)