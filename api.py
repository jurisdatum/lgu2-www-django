
import requests

_server = 'http://localhost:8080/'

def browse_by_type(type: str, page: str):
    url = _server + 'documents/' + type + '?page=' + page
    headers = { 'Accept': 'application/json' }
    return requests.get(url, headers=headers).json()

def get_document(type: str, year, number):
    url = _server + 'document/' + type + '/' + str(year) + '/' + str(number)
    headers = { 'Accept': 'application/json' }
    return requests.get(url, headers=headers).json()
