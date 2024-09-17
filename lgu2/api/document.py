
import requests
from typing import List, TypedDict

from .server import SERVER

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

def get_document(type: str, year, number, version=None) -> Document:
    url = SERVER + '/document/' + type + '/' + str(year) + '/' + str(number)
    if version:
        url += '/' + version
    headers = { 'Accept': 'application/json' }
    return requests.get(url, headers=headers).json()

def get_clml(type: str, year, number, version=None):
    url = SERVER + '/document/' + type + '/' + str(year) + '/' + str(number)
    if version:
        url += '/' + version
    headers = { 'Accept': 'application/xml' }
    return requests.get(url, headers=headers)

def get_akn(type: str, year, number, version=None):
    url = SERVER + '/document/' + type + '/' + str(year) + '/' + str(number)
    if version:
        url += '/' + version
    headers = { 'Accept': 'application/akn+xml' }
    return requests.get(url, headers=headers)
