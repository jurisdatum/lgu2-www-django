
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

def get_uk_types() -> Response:
    url = '/types/uk'
    return server.get_json(url)
