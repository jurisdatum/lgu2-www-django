
from . import server
from .document import Document

def _make_url(type: str, year, number, section: str, version=None) -> str:
    url = '/fragment/' + type + '/' + str(year) + '/' + str(number)
    url += '/' + section.replace('/', '-')
    if version:
        url += '?version=' + version
    return url

def get(type: str, year, number, section: str, version=None) -> Document:
    url = _make_url(type, year, number, section, version)
    return server.get_json(url)

def get_clml(type: str, year, number, section: str, version=None) -> str:
    url = _make_url(type, year, number, section, version)
    return server.get_clml(url)

def get_akn(type: str, year, number, section: str, version=None) -> str:
    url = _make_url(type, year, number, section, version)
    return server.get_akn(url)
