from typing import TypedDict, Optional, List, Dict, Union, Any


class QueryParams(TypedDict, total=False):
    year: Optional[int]
    type: Optional[str]
    subject: Optional[str]
    pageSize: Optional[int]
    sort: Optional[str]
    page: Optional[int]
    title: Optional[str]
    number: Union[str, int]

class SearchResultContext(TypedDict):
    meta_data: Dict[str, Any]
    documents_data: List[Any]
    grouped_documents: Optional[Dict[str, List[Any]]]
    page_range: range
    current_page: int
    total_pages: int
    current_subject: Optional[str]
    subject_heading: Optional[str]
    total_count_by_type: int
    total_count_by_year: int
    modified_query_links: Dict[str, str]
    query_params: str
    query_param: QueryParams
    by_year_pagination_count: int
    current_year: str
    current_type: Optional[str]
    grouped_by_decade: bool
    subject_initials: Optional[set[str]]
    all_lowercase_letters: str
    default_pagesize: int




