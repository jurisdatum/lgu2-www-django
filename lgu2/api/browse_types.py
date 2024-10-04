
from typing import List, TypedDict

class DocumentList(TypedDict):
    meta: 'ListMeta'
    documents: List['DocEntry']

class ListMeta:
    page: int
    pageSize: int
    totalPages: int
    updated: str # dateTime
    counts: 'Counts'

class Counts:
    total: int
    byType: List['ByType']
    yearly: List['ByYear']
    subjects: 'Subjects'

class ByType:
    type: str
    count: int

class ByYear:
    year: int
    count: int

class Subjects:
    byInitial: List['ByInitial']
    headings: List[str]

class ByInitial:
    initial: str
    count: int

class DocEntry(TypedDict):
    id: str
    longType: str
    year: int
    number: int
    altNumbers: List['AltNumber']
    cite: str
    title: str
    altTitle: str
    published: str # dateTime
    updated: str #dateTime
    version: str

class AltNumber(TypedDict):
    category: str
    value: str


