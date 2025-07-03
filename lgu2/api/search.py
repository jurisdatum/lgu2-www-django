from django.conf import settings
import requests

SERVER = settings.API_BASE_URL


def basic_search(query_params):

    query_param = query_params.GET.dict()
    query_params = {key: value for key, value in query_param.items() if value}
    api_url = SERVER+'/search'
    
    response = requests.get(api_url, params=query_params)
    api_data = response.json() if response.status_code == 200 else {}

    query_params = {key: value for key, value in query_param.items()}
    print(query_params)
    return api_data, query_params
