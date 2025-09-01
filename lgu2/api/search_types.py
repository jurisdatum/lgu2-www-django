from typing import NotRequired, TypedDict


class SearchParams(TypedDict):
    """Search parameters for the /search API endpoint.

    Note: All parameters mirror the external API contract exactly.
    The 'number' field accepts string-based legislation references
    (e.g., "1", "w2", "ni15") not just numeric IDs.
    """
    year: NotRequired[int]
    type: NotRequired[str]
    subject: NotRequired[str]
    pageSize: NotRequired[int]
    sort: NotRequired[str]
    page: NotRequired[int]
    title: NotRequired[str]
    number: NotRequired[str]
