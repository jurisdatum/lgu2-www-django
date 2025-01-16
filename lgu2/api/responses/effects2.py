
from typing import List, NotRequired, Optional, TypedDict


class RichTextNode(TypedDict):
    type: str  # text or link
    text: str
    id: NotRequired[str]  # fragment id, absent if type is text
    href: NotRequired[str]  # absent if type is text
    missing: NotRequired[bool]  # absent if type is text, can also be absent if link is not missing


class Provisions(TypedDict):
    plain: str
    rich: List[RichTextNode]


class Source(TypedDict):
    id: str  # document id
    longType: str
    year: int
    number: int
    title: str
    provisions: Provisions


class InForceDate(TypedDict):
    date: Optional[str]  # None if prospective is True?
    applied: bool
    prospective: NotRequired[bool]  # True if date is None?
    description: NotRequired[str]


class Effect(TypedDict):
    applied: bool
    required: bool
    type: str
    target: Source
    source: Source
    inForceDates: List[InForceDate]
    commencement: Provisions
    notes: Optional[str]


class Metadata(TypedDict):
    page: int
    pageSize: int
    totalPages: int
    startIndex: int
    totalResults: int
    updated: str


class Page(TypedDict):
    meta: Metadata
    effects: List[Effect]
