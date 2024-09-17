
import requests

from .server import SERVER

def get_metadata(type: str, year, number):
    url = SERVER + '/metadata/' + type + '/' + str(year) + '/' + str(number)
    headers = { 'Accept': 'application/json' }
    return requests.get(url, headers=headers).json()
