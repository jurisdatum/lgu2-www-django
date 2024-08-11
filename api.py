
import requests

_server = 'http://localhost:8080/'

def browse_by_type(type: str, page: str):
    return requests.get(_server + 'documents/' + type + '?page=' + page).json()

def get_document(type: str, year, number):
    return requests.get(_server + 'document/' + type + '/' + str(year) + '/' + str(number) + '/data.html').text
