
from typing import List, TypedDict

from . import server
from .document import CommonMetadata, DocumentMetadata


class Provision(TypedDict):
    id: str
    href: str
    label: str
    title: str


class ExtendedMetadata(DocumentMetadata):
    confersPower: List[Provision]
    blanketAmendments: List[Provision]


def get_metadata(type: str, year, number):
    url = '/metadata/' + type + '/' + str(year) + '/' + str(number)
    meta = server.get_json(url)
    CommonMetadata.convert_dates(meta)
    return meta
