
from typing import List, Optional, TypedDict
from urllib.parse import urlencode

from lgu2.api.responses.effects import UnappliedEffect

from . import server
from .document import CommonMetadata, XmlPackage, package_xml


class FragmentMetadata(CommonMetadata):
    fragment: str
    prev: Optional[str]
    next: Optional[str]
    unappliedEffects: 'FragmentEffects'


class FragmentEffects(TypedDict):
    fragment: List[UnappliedEffect]
    ancestor: List[UnappliedEffect]


class Fragment(TypedDict):
    meta: FragmentMetadata
    html: str


def _make_url(type: str, year, number, section: str, version=None, language: Optional[str] = None) -> str:
    url = '/fragment/' + type + '/' + str(year) + '/' + str(number)
    url += '/' + section.replace('/', '-')
    params = {'version': version, 'language': language}
    params = {k: v for k, v in params.items() if v is not None}
    if params:
        url += '?' + urlencode(params)
    return url


def get(type: str, year, number, section: str, version=None, language: Optional[str] = None) -> Fragment:
    url = _make_url(type, year, number, section, version, language)
    return server.get_json(url)


def get_clml(type: str, year, number, section: str, version=None, language: Optional[str] = None) -> XmlPackage:
    url = _make_url(type, year, number, section, version, language)
    response = server.get_clml(url)
    return package_xml(response)


def get_akn(type: str, year, number, section: str, version=None, language: Optional[str] = None) -> XmlPackage:
    url = _make_url(type, year, number, section, version, language)
    response = server.get_akn(url)
    return package_xml(response)
