
import requests

_server = 'http://localhost:8080/'


def browse_by_type(type: str, page: str):
    url = _server + 'documents/' + type + '?page=' + page
    headers = { 'Accept': 'application/json' }
    return requests.get(url, headers=headers).json()

def browse_by_type_and_year(type: str, year: int, page: str):
    url = _server + 'documents/' + type + '/' + str(year) + '?page=' + page
    headers = { 'Accept': 'application/json' }
    return requests.get(url, headers=headers).json()

# documents

def get_document(type: str, year, number, version=None):
    url = _server + 'document/' + type + '/' + str(year) + '/' + str(number)
    if version:
        url += '/' + version
    headers = { 'Accept': 'application/json' }
    return requests.get(url, headers=headers).json()

def get_clml(type: str, year, number, version=None):
    url = _server + 'document/' + type + '/' + str(year) + '/' + str(number)
    if version:
        url += '/' + version
    headers = { 'Accept': 'application/xml' }
    return requests.get(url, headers=headers)

def get_akn(type: str, year, number, version=None):
    url = _server + 'document/' + type + '/' + str(year) + '/' + str(number)
    if version:
        url += '/' + version
    headers = { 'Accept': 'application/akn+xml' }
    return requests.get(url, headers=headers)

# metadata

def get_metadata(type: str, year, number):
    url = _server + 'metadata/' + type + '/' + str(year) + '/' + str(number)
    headers = { 'Accept': 'application/json' }
    return requests.get(url, headers=headers).json()
