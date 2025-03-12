
from typing import List, TypedDict

from . import server


class Response(TypedDict):
    country: str
    primarily: List['Type']
    possibly: List['Type']


class Type(TypedDict):
    shortName: str
    longName: str
    category: str


def get_types(country: str) -> Response:
    url = '/types/' + country
    return server.get_json(url)
