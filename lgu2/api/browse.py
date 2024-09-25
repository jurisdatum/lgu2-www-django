
from . import server

def browse_by_type(type: str, page: str):
    url = '/documents/' + type + '?page=' + page
    return server.get_json(url)

def browse_by_type_and_year(type: str, year: int, page: str):
    url = '/documents/' + type + '/' + str(year) + '?page=' + page
    return server.get_json(url)
