from typing import List, NotRequired, TypedDict, Union


class ApiSearchRequest(TypedDict):
    """Request shape for the /search endpoint.

    Mirrors the API contract exactly; field names match the wire format
    (e.g. `q` for the keyword field, not the view-side alias `text`).
    """
    year: NotRequired[int]
    startYear: NotRequired[int]
    endYear: NotRequired[int]
    type: NotRequired[Union[str, List[str]]]
    subject: NotRequired[str]
    pageSize: NotRequired[int]
    sort: NotRequired[str]
    page: NotRequired[int]
    title: NotRequired[str]
    number: NotRequired[str]
    q: NotRequired[str]
    language: NotRequired[str]
    pointInTime: NotRequired[str]
    extent: NotRequired[List[str]]
    exclusiveExtent: NotRequired[bool]
    stage: NotRequired[str]
    department: NotRequired[str]
    ukAmended: NotRequired[bool]
