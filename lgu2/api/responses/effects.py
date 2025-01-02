
from typing import List, NotRequired, Optional, TypedDict


class Effect(TypedDict):
    required: bool
    type: str
    affected: 'Provisions'
    inForceDates: List['InForceDate']
    source: 'Source'
    commencement: 'Provisions'
    notes: Optional[str]


class Provisions(TypedDict):
    plain: str
    rich: List['RichTextNode']


class RichTextNode(TypedDict):
    type: str  # text or link
    text: str
    id: NotRequired[str]  # fragment id, absent if type is text
    href: NotRequired[str]  # absent if type is text
    missing: NotRequired[bool]  # absent if type is text, can also be absent if link is not missing


class InForceDate(TypedDict):
    date: Optional[str]  # None if prospective is True?
    applied: bool
    prospective: NotRequired[bool]  # True if date is None?
    description: NotRequired[str]


class Source(TypedDict):
    id: str  # document id
    longType: str
    year: int
    number: int
    provisions: Provisions
