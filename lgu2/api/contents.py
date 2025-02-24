
from typing import List, Optional, TypedDict
from urllib.parse import urlencode

from . import server
from .document import DocumentMetadata, XmlPackage, package_xml


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
    meta: DocumentMetadata
    html: str


def _make_url(type: str, year, number, version: Optional[str] = None) -> str:
    url = '/contents/' + type + '/' + str(year) + '/' + str(number)
    if version is not None:
        params = {'version': version}
        url += '?' + urlencode(params)
    return url


def get_toc(type: str, year, number, version: Optional[str] = None, language: Optional[str] = None) -> dict:
    url = _make_url(type, year, number, version)
    return server.get_json(url, language)


def get_toc_json(type: str, year, number, version: Optional[str] = None, language: Optional[str] = None) -> str:
    url = _make_url(type, year, number, version)
    return server.get_raw_json(url, language)


def get_toc_clml(type: str, year, number, version: Optional[str] = None, language: Optional[str] = None) -> XmlPackage:
    url = _make_url(type, year, number, version)
    response = server.get_clml(url, language)
    return package_xml(response)


def get_toc_akn(type: str, year, number, version: Optional[str] = None, language: Optional[str] = None) -> XmlPackage:
    url = _make_url(type, year, number, version)
    response = server.get_akn(url, language)
    return package_xml(response)
