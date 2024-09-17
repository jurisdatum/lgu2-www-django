
from typing import List, TypedDict

from .document import Meta
from .server import *

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
    attachmentsBeforeSchedules: List[Item] # EU only
    schedules: List[Item]
    attachments: List[Item]

class Response(TypedDict):
    meta: Meta
    html: str

def _make_url(type: str, year, number, version=None) -> str:
    url = '/contents/' + type + '/' + str(year) + '/' + str(number)
    if version:
        url += '?version=' + version
    return url

def get_toc(type: str, year, number, version=None) -> dict:
    url = _make_url(type, year, number, version)
    return get_json(url)

def get_toc_json(type: str, year, number, version=None) -> str:
    url = _make_url(type, year, number, version)
    return get_raw_json(url)

def get_toc_clml(type: str, year, number, version=None) -> str:
    url = _make_url(type, year, number, version)
    return get_clml(url)

def get_toc_akn(type: str, year, number, version=None) -> str:
    url = _make_url(type, year, number, version)
    return get_akn(url)
