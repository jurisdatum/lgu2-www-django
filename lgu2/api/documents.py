
from datetime import datetime, timezone

from . import server
from .browse_types import DocumentList


def get_new() -> DocumentList:
    url = '/documents/new/all'
    raw = server.get_json(url)
    for doc in raw['documents']:
        doc['published'] = datetime.fromisoformat(doc['published']).astimezone(timezone.utc)
    return raw
