
from . import server
from .browse_types import DocumentList


def browse_by_type(type: str, page: str) -> DocumentList:
    url = '/documents/' + type + '?page=' + page
    # ToDo convert dates
    return server.get_json(url)


def browse_by_type_and_year(type: str, year, page: str) -> DocumentList:
    url = '/documents/' + type + '/' + str(year) + '?page=' + page
    # ToDo convert dates
    return server.get_json(url)
