
from typing import List, NotRequired, Optional, TypedDict
from urllib.parse import urlencode

from lgu2.api.responses.effects import Effect

from . import server
from .document import CommonMetadata, XmlPackage, package_xml


class FragmentMetadata(CommonMetadata):
    fragment: str
    prev: Optional[str]
    next: Optional[str]
    fragmentInfo: 'Level'
    ancestors: List['Level']
    descendants: List['Level']
    pointInTime: Optional[str]
    unappliedEffects: 'FragmentEffects'
    upToDate: Optional[bool]


class Level(TypedDict):
    element: str
    id: str
    href: str
    number: str
    title: str
    label: str


class FragmentEffects(TypedDict):
    fragment: List[Effect]
    ancestor: List[Effect]


class Fragment(TypedDict):
    meta: FragmentMetadata
    html: str


def _make_url(type: str, year, number, section: str, version: Optional[str] = None) -> str:
    url = '/fragment/' + type + '/' + str(year) + '/' + str(number)
    url += '/' + section.replace('/', '-')
    if version is not None:
        params = {'version': version}
        url += '?' + urlencode(params)
    return url


def get(type: str, year, number, section: str, version: Optional[str] = None, language: Optional[str] = None) -> Fragment:
    url = _make_url(type, year, number, section, version)
    return server.get_json(url, language)


def get_clml(type: str, year, number, section: str, version: Optional[str] = None, language: Optional[str] = None) -> XmlPackage:
    url = _make_url(type, year, number, section, version)
    response = server.get_clml(url, language)
    return package_xml(response)


def get_akn(type: str, year, number, section: str, version: Optional[str] = None, language: Optional[str] = None) -> XmlPackage:
    url = _make_url(type, year, number, section, version)
    response = server.get_akn(url, language)
    return package_xml(response)
