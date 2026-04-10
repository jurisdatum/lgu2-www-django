
from datetime import date as Date
from typing import List, TypedDict, Optional, NotRequired


class AltFormat(TypedDict):
    url: str
    thumbnail: Optional[str]
    label: str
    language: str
    type: str  # MIME type e.g. 'application/pdf'
    date: Optional[Date]
    size: Optional[int]


class DocRef(TypedDict):
    id: str
    shortType: str
    longType: str
    year: int
    number: int
    regnalYear: NotRequired[str]


class AssociatedDocumentMeta(TypedDict):
    id: str
    shortType: str
    longType: str
    year: int
    number: int
    regnalYear: NotRequired[str]
    title: str
    modified: Date
    associatedWith: DocRef
    altFormats: List[AltFormat]

    @staticmethod
    def convert_dates(meta: 'AssociatedDocumentMeta'):
        meta['modified'] = Date.fromisoformat(meta['modified'])


class ImpactAssessmentMeta(AssociatedDocumentMeta):
    stage: str
    department: str


class AssociatedDocument(TypedDict):
    meta: AssociatedDocumentMeta
