"""View-side search parameter shape and the translator that prepares it
for the API client.

`SearchParams` is the shape views build to describe a search. It uses
view-friendly names (e.g. `text` for the keyword field), which the
translator below maps onto the API's contract before forwarding.
"""
from typing import List, NotRequired, TypedDict, Union

from ..api.browse_types import DocumentList
from ..api.search_types import ApiSearchRequest


class SearchParams(TypedDict):
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
    text: NotRequired[str]
    language: NotRequired[str]
    pointInTime: NotRequired[str]
    extent: NotRequired[List[str]]
    exclusiveExtent: NotRequired[bool]
    stage: NotRequired[str]
    department: NotRequired[str]
    ukAmended: NotRequired[bool]


# View-side key → API-side key renames. Single source of truth for the
# name divergences between SearchParams and ApiSearchRequest.
_VIEW_TO_API = {"text": "q"}
_API_TO_VIEW = {v: k for k, v in _VIEW_TO_API.items()}


def to_api_request(params: SearchParams) -> ApiSearchRequest:
    """Translate a view-side SearchParams into the API's request shape."""
    return {_VIEW_TO_API.get(k, k): v for k, v in params.items()}  # type: ignore[return-value]


def from_api_response(response: DocumentList) -> DocumentList:
    """Translate an API search response into the view-side shape.

    Renames `meta.query` keys back to view-side names (e.g. `q` → `text`)
    so view-side consumers see the same keys they used to build the
    request. Returns a new object; the input is not mutated.
    """
    out: DocumentList = {**response, "meta": {**response["meta"]}}
    query = response["meta"].get("query")
    if query is not None:
        out["meta"]["query"] = {_API_TO_VIEW.get(k, k): v for k, v in query.items()}
    return out
