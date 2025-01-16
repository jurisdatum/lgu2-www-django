
from typing import Optional
from urllib.parse import urlencode

from .responses.effects2 import Page

from . import server


def _make_url(**kwargs) -> str:
    params = {k: v for k, v in kwargs.items() if v is not None}
    return '/effects?' + urlencode(params)


def fetch(
    targetType: Optional[str] = None,
    targetYear: Optional[str] = None,
    targetNumber: Optional[int] = None,
    targetTitle: Optional[str] = None
) -> Page:
    url = _make_url(**locals())
    return server.get_json(url)


# def fetch_atom(
#     targetType: Optional[str] = None,
#     targetYear: Optional[str] = None,
#     targetNumber: Optional[int] = None,
#     targetTitle: Optional[str] = None
# ):
#     url = _make_url(**locals())
#     return server.get_json(url)
