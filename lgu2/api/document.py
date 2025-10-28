
from datetime import date as Date
from typing import List, Optional, TypedDict, NotRequired, Literal
from urllib.parse import urlencode

from . import server
from .browse_types import AltNumber
from .responses.effects import Effect

Extent = Literal['E', 'W', 'S', 'NI', 'EU']

AssociatedDocumentType = Literal[
    'Note', 'PolicyEqualityStatement', 'Alternative', 'CorrectionSlip',
    'CodeOfPractice', 'CodeOfConduct', 'TableOfOrigins', 'TableOfDestinations',
    'OrderInCouncil', 'ImpactAssessment', 'Other', 'ExplanatoryDocument',
    'TranspositionNote', 'UKRPCOpinion'
]

class AssociatedDocument(TypedDict):
    type: AssociatedDocumentType
    uri: str
    name: NotRequired[str]
    date: NotRequired[Date]
    size: NotRequired[int]


class Has(TypedDict):
    introduction: NotRequired[bool]
    signature: NotRequired[bool]
    schedules: NotRequired[bool]
    note: NotRequired[bool]


class CommonMetadata(TypedDict):
    id: str
    longType: str
    shortType: str
    year: int
    regnalYear: NotRequired[str]
    number: int
    altNumbers: NotRequired[List[AltNumber]]
    isbn: NotRequired[str]
    date: Optional[Date]
    cite: str
    version: str
    status: Literal['final', 'revised']
    title: str
    extent: List[Extent]
    subjects: NotRequired[List[str]]
    lang: str
    publisher: str
    modified: Date
    versions: List[str]  # SortedSet in Java
    has: Has
    schedules: bool  # deprecated in Java but still present
    formats: List[str]
    pointInTime: NotRequired[Date]
    alternatives: List[AssociatedDocument]
    associated: List[AssociatedDocument]

    @staticmethod
    def convert_dates(meta: 'CommonMetadata'):
        if meta.get('date'):  # can be null
            meta['date'] = Date.fromisoformat(meta['date'])
        meta['modified'] = Date.fromisoformat(meta['modified'])
        if meta.get('pointInTime'):  # can be null
            meta['pointInTime'] = Date.fromisoformat(meta['pointInTime'])


class DocumentMetadata(CommonMetadata):
    unappliedEffects: List[Effect]
    upToDate: NotRequired[bool]


class Document(TypedDict):
    meta: DocumentMetadata
    html: str


class Redirect(TypedDict):
    type: str  # short type
    year: str  # calendar or regnal
    number: str
    version: Optional[str]  # None if 'current'


class XmlPackage(TypedDict):
    xml: str
    redirect: Optional[Redirect]  # None if all request parameters were canonical


def _make_url(type: str, year, number, version: Optional[str] = None) -> str:
    url = '/document/' + type + '/' + str(year) + '/' + str(number)
    if version is not None:
        params = {'version': version}
        url += '?' + urlencode(params)
    return url


def get_document(type: str, year, number, version: Optional[str] = None, language: Optional[str] = None) -> Document:
    url = _make_url(type, year, number, version)
    doc = server.get_json(url, language)
    CommonMetadata.convert_dates(doc['meta'])
    return doc


def package_xml(response) -> XmlPackage:
    try:
        redirect = {
            'type': response.headers['X-Document-Type'],
            'year': response.headers['X-Document-Year'],
            'number': response.headers['X-Document-Number'],
            'version': None if response.headers['X-Document-Version'] == 'current' else response.headers['X-Document-Version']
        }
    except KeyError:
        redirect = None
    return {'xml': response.text, 'redirect': redirect}


def get_clml(type: str, year, number, version: Optional[str] = None, language: Optional[str] = None) -> XmlPackage:
    url = _make_url(type, year, number, version)
    response = server.get_clml(url, language)
    return package_xml(response)


def get_akn(type: str, year, number, version: Optional[str] = None, language: Optional[str] = None) -> XmlPackage:
    url = _make_url(type, year, number, version)
    response = server.get_akn(url, language)
    return package_xml(response)
