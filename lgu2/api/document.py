
from typing import List, TypedDict

from .server import *

class Meta(TypedDict):
    id: str
    longType: str
    shortType: str
    year: int
    regnalYear: str
    number: int
    date: str
    cite: str
    version: str
    status: str
    title: str
    lang: str
    publisher: str
    modified: str
    versions: List[str]

class Document(TypedDict):
    meta: Meta
    html: str

def _make_url(type: str, year, number, version=None) -> str:
    url = '/document/' + type + '/' + str(year) + '/' + str(number)
    if version:
        url += '?version=' + version
    return url

def get_document(type: str, year, number, version=None) -> Document:
    url = _make_url(type, year, number, version)
    return get_json(url)

def get_clml(type: str, year, number, version=None) -> str:
    url = _make_url(type, year, number, version)
    return get_clml(url)

def get_akn(type: str, year, number, version=None) -> str:
    url = _make_url(type, year, number, version)
    return get_akn(url)
