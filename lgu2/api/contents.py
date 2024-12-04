
from typing import List, Optional, TypedDict
from urllib.parse import urlencode

from . import server
from .document import Meta, XmlPackage, package_xml


class Item(TypedDict):
    name: str
    number: str
    title: str
    ref: str
    children: List['Item']


class Contents(TypedDict):
    title: str
    body: List[Item]
    appendices: List[Item]
    attachmentsBeforeSchedules: List[Item]  # EU only
    schedules: List[Item]
    attachments: List[Item]


class Response(TypedDict):
    meta: Meta
    html: str


def _make_url(type: str, year, number, version: Optional[str] = None, language: Optional[str] = None) -> str:
    url = '/contents/' + type + '/' + str(year) + '/' + str(number)
    params = {'version': version, 'language': language}
    params = {k: v for k, v in params.items() if v is not None}
    if params:
        url += '?' + urlencode(params)
    return url


def get_toc(type: str, year, number, version: Optional[str] = None, language: Optional[str] = None) -> dict:
    url = _make_url(type, year, number, version, language)
    return server.get_json(url)


def get_toc_json(type: str, year, number, version: Optional[str] = None, language: Optional[str] = None) -> str:
    url = _make_url(type, year, number, version, language)
    return server.get_raw_json(url)


def get_toc_clml(type: str, year, number, version: Optional[str] = None, language: Optional[str] = None) -> XmlPackage:
    url = _make_url(type, year, number, version, language)
    response = server.get_clml(url)
    return package_xml(response)


def get_toc_akn(type: str, year, number, version: Optional[str] = None, language: Optional[str] = None) -> XmlPackage:
    url = _make_url(type, year, number, version, language)
    response = server.get_akn(url)
    return package_xml(response)
