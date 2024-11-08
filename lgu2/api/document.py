
from typing import List, Optional, TypedDict
from urllib.parse import urlencode

from . import server
from .browse_types import AltNumber


class Meta(TypedDict):
    id: str
    longType: str
    shortType: str
    year: int
    regnalYear: str
    number: int
    altNumbers: List[AltNumber]
    date: str
    cite: str
    version: str
    status: str
    title: str
    lang: str
    publisher: str
    modified: str
    versions: List[str]
    schedules: bool
    formats: List[str]


class Document(TypedDict):
    meta: Meta
    html: str


def _make_url(type: str, year, number, version: Optional[str] = None, language: Optional[str] = None) -> str:
    url = '/document/' + type + '/' + str(year) + '/' + str(number)
    params = {'version': version, 'language': language}
    params = {k: v for k, v in params.items() if v is not None}
    if params:
        url += '?' + urlencode(params)
    return url


def get_document(type: str, year, number, version: Optional[str] = None, language: Optional[str] = None) -> Document:
    url = _make_url(type, year, number, version, language)
    return server.get_json(url)


def get_clml(type: str, year, number, version: Optional[str] = None, language: Optional[str] = None) -> str:
    url = _make_url(type, year, number, version, language)
    return server.get_clml(url)


def get_akn(type: str, year, number, version: Optional[str] = None, language: Optional[str] = None) -> str:
    url = _make_url(type, year, number, version, language)
    return server.get_akn(url)
