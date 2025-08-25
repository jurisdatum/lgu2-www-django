
from datetime import datetime, timezone
from typing import List, TypedDict, Optional, Collection, Dict, Any, NotRequired


def _to_utc(ts: str) -> datetime:
    """Parse an ISO-8601 timestamp and normalise it to UTC."""
    return datetime.fromisoformat(ts).astimezone(timezone.utc)


class DocumentList(TypedDict):
    meta: 'ListMeta'
    documents: List['DocEntry']

    @staticmethod
    def convert_dates(doc_list: 'DocumentList'):
        doc_list['meta']['updated'] = _to_utc(doc_list['meta']['updated'])
        for doc in doc_list['documents']:
            doc['published'] = _to_utc(doc['published'])
            doc['updated'] = _to_utc(doc['updated'])


class ListMeta(TypedDict):
    query: NotRequired[Dict[str, Any]]
    page: int
    pageSize: int
    totalPages: int
    updated: datetime
    counts: 'Counts'
    subjects: NotRequired[Collection[str]]


class Counts(TypedDict):
    total: int
    byType: List['ByType']
    byYear: List['ByYear']
    bySubjectInitial: List['ByInitial']


class ByType(TypedDict):
    type: str
    count: int


class ByYear(TypedDict):
    year: int
    count: int


class ByInitial(TypedDict):
    initial: str
    count: int


class DocEntry(TypedDict):
    id: str
    longType: str
    year: int
    number: Optional[int]
    altNumbers: List['AltNumber']
    isbn: NotRequired[str]
    cite: str
    title: str
    altTitle: NotRequired[str]
    description: NotRequired[str]
    subjects: NotRequired[List[str]]
    published: datetime
    updated: datetime
    version: str
    formats: List[str]


class AltNumber(TypedDict):
    category: str
    value: str
