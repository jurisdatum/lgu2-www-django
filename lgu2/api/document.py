
from typing import List, Optional, TypedDict
from urllib.parse import urlencode

from . import server
from .browse_types import AltNumber
from .responses.effects import Effect


class CommonMetadata(TypedDict):
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


class DocumentMetadata(CommonMetadata):
    unappliedEffects: List[Effect]


class Document(TypedDict):
    meta: DocumentMetadata
    html: str


class Redirect(TypedDict):
    type: str  # short type
    year: str  # calendar or regnal
    number: str
    version: Optional[str]  # None if 'current'


class XmlPackage(TypedDict):
    xml: str
    redirect: Optional[Redirect]  # None if all request parameters were canonical


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


def package_xml(response) -> XmlPackage:
    try:
        redirect = {
            'type': response.headers['X-Document-Type'],
            'year': response.headers['X-Document-Year'],
            'number': response.headers['X-Document-Number'],
            'version': None if response.headers['X-Document-Version'] == 'current' else response.headers['X-Document-Version']
        }
    except KeyError:
        redirect = None
    return {'xml': response.text, 'redirect': redirect}


def get_clml(type: str, year, number, version: Optional[str] = None, language: Optional[str] = None) -> XmlPackage:
    url = _make_url(type, year, number, version, language)
    response = server.get_clml(url)
    return package_xml(response)


def get_akn(type: str, year, number, version: Optional[str] = None, language: Optional[str] = None) -> XmlPackage:
    url = _make_url(type, year, number, version, language)
    response = server.get_akn(url)
    return package_xml(response)
