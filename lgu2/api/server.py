
import requests

from django.conf import settings

SERVER = settings.API_BASE_URL

def get(endpoint: str, accept: str) -> requests.Response:
    url = SERVER + endpoint
    headers = { 'Accept': accept }
    return requests.get(url, headers=headers)

def get_json(endpoint: str):
    return get(endpoint, 'application/json').json()

def get_raw_json(endpoint: str) -> str:
    return get(endpoint, 'application/json').text

def get_clml(endpoint: str) -> str:
    return get(endpoint, 'application/xml').text

def get_akn(endpoint: str) -> str:
    return get(endpoint, 'application/akn+xml').text
