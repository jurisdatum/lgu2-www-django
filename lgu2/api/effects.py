
from typing import Optional
from urllib.parse import urlencode

from .responses.effects import Page

from . import server


def _make_url(**kwargs) -> str:
    params = {k: v for k, v in kwargs.items() if v is not None}
    return '/effects?' + urlencode(params)


def fetch(
    targetType: Optional[str] = None,
    targetYear: Optional[int] = None,
    targetStartYear: Optional[int] = None,
    targetEndYear: Optional[int] = None,
    targetNumber: Optional[int] = None,
    targetTitle: Optional[str] = None,
    sourceType: Optional[str] = None,
    sourceYear: Optional[int] = None,
    sourceStartYear: Optional[int] = None,
    sourceEndYear: Optional[int] = None,
    sourceNumber: Optional[int] = None,
    sourceTitle: Optional[str] = None,
    applied: Optional[str] = None,
    page: int = 1
) -> Page:
    url = _make_url(**locals())
    return server.get_json(url)


def fetch_atom(
    targetType: Optional[str] = None,
    targetYear: Optional[int] = None,
    targetNumber: Optional[int] = None,
    targetTitle: Optional[str] = None,
    sourceType: Optional[str] = None,
    sourceYear: Optional[int] = None,
    sourceNumber: Optional[int] = None,
    sourceTitle: Optional[str] = None,
    page: int = 1
) -> str:
    url = _make_url(**locals())
    return server.get(url, 'application/atom+xml').text
