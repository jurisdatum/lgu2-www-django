
from typing import Optional, Union

from .server import SERVER


Number = Union[str, int]


def make_pdf_url(type: str, year: Number, number: Number, version: Optional[str] = None) -> str:
    url = SERVER + '/pdf/' + type + '/' + str(year) + '/' + str(number)
    if version:
        url += '?version=' + version
    return url


def make_thumbnail_url(type: str, year: Number, number: Number, version: Optional[str] = None) -> str:
    url = SERVER + '/thumbnail/' + type + '/' + str(year) + '/' + str(number)
    if version:
        url += '?version=' + version
    return url
