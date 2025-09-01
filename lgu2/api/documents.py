
from datetime import datetime, timezone
from typing import Optional

from . import server
from .browse_types import DocumentList


def _to_utc(ts: str) -> datetime:
    """Parse an ISO-8601 timestamp and normalise it to UTC."""
    return datetime.fromisoformat(ts).astimezone(timezone.utc)


def _convert_dates(doc):
    doc['updated'] = _to_utc(doc['updated'])
    doc['published'] = _to_utc(doc['published'])


def get_new() -> DocumentList:
    url = '/documents/new/all'
    response = server.get_json(url)
    response['meta']['updated'] = _to_utc(response['meta']['updated'])
    for doc in response['documents']:
        _convert_dates(doc)
    return response


def get_published_on(date: str, region: Optional[str] = None) -> DocumentList:
    url = f'/search?published={date}'
    if region:
        url += '&type=' + region
    response = server.get_json(url)
    response['meta']['updated'] = _to_utc(response['meta']['updated'])
    for doc in response['documents']:
        _convert_dates(doc)
    return response
