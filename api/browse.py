
import requests

from .server import SERVER

def browse_by_type(type: str, page: str):
    url = SERVER + '/documents/' + type + '?page=' + page
    headers = { 'Accept': 'application/json' }
    return requests.get(url, headers=headers).json()

def browse_by_type_and_year(type: str, year: int, page: str):
    url = SERVER + '/documents/' + type + '/' + str(year) + '?page=' + page
    headers = { 'Accept': 'application/json' }
    return requests.get(url, headers=headers).json()
