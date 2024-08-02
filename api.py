
import requests

_server = 'http://localhost:8080/'

def browse_by_type(type: str):
    return requests.get(_server + 'documents/' + type).json()
