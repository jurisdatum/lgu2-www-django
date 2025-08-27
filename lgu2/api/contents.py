
from datetime import date
from typing import List, NotRequired, Optional, TypedDict, Union, Literal
from urllib.parse import urlencode

from . import server
from .document import DocumentMetadata, XmlPackage, package_xml, Extent

class Item(TypedDict):
    name: str
    number: str
    title: str
    ref: str
    extent: NotRequired[List[Extent]]
    children: NotRequired[List['Item']]


class Contents(TypedDict):
    title: str
    introduction: NotRequired[Item]
    body: List[Item]
    signature: NotRequired[Item]
    appendices: NotRequired[List[Item]]
    attachmentsBeforeSchedules: NotRequired[List[Item]]  # EU only
    schedules: NotRequired[List[Item]]
    attachments: NotRequired[List[Item]]
    explanatoryNote: NotRequired[Item]
    earlierOrders: NotRequired[Item]


class TableOfContents(TypedDict):
    meta: DocumentMetadata
    contents: Contents


def _make_url(type: str, year, number, version: Optional[str] = None) -> str:
    url = '/contents/' + type + '/' + str(year) + '/' + str(number)
    if version is not None:
        params = {'version': version}
        url += '?' + urlencode(params)
    return url


def get_toc(type: str, year, number, version: Optional[str] = None, language: Optional[str] = None) -> Optional[TableOfContents]:
    url = _make_url(type, year, number, version)
    toc = server.get_json(url, language)
    # Check if response is a "404" document-not-found type
    if toc.get('status') == 404 and toc.get('error') == "Document Not Found":
        return None

    if toc['meta']['date']:
        toc['meta']['date'] = date.fromisoformat(toc['meta']['date'])
    return toc


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
