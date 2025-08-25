from django.shortcuts import render
from urllib.parse import urlencode
from collections import defaultdict
from typing import TypedDict, Optional, List, Dict, Any
from ..api.search import basic_search
from ..util.cutoff import get_cutoff
from ..api.search_types import SearchParams
import string


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
    query_param: SearchParams
    by_year_pagination_count: int
    current_year: str
    current_type: Optional[str]
    grouped_by_decade: bool
    subject_initials: Optional[set[str]]
    all_lowercase_letters: str
    default_pagesize: int


def extract_query_params(request) -> SearchParams:
    params: SearchParams = {}

    if "sort" in request.GET and request.GET["sort"].strip():
        params["sort"] = request.GET["sort"].strip()

    if "pageSize" in request.GET and request.GET["pageSize"].isdigit():
        params["pageSize"] = int(request.GET["pageSize"])

    if "page" in request.GET and request.GET["page"].isdigit():
        params["page"] = int(request.GET["page"])

    if "subject" in request.GET and request.GET["subject"].strip():
        params["subject"] = request.GET["subject"].strip()

    if "year" in request.GET and request.GET["year"].isdigit():
        params["year"] = int(request.GET["year"])

    if "type" in request.GET and request.GET["type"].strip():
        params["type"] = request.GET["type"].strip()

    if "title" in request.GET and request.GET["title"].strip():
        params["title"] = request.GET["title"].strip()

    if "number" in request.GET and request.GET["number"].strip():
        params["number"] = request.GET["number"].strip()

    return params


def search_results(request):
    # Step 1: Clean and extract query parameters
    query_params: SearchParams = extract_query_params(request)

    # Step 2: Fetch data using cleaned parameters
    api_data_raw = basic_search(query_params)

    meta = api_data_raw.get("meta", {})
    documents_data = api_data_raw.get("documents", [])

    # Step 3: Count totals
    total_count_by_type = sum(item["count"] for item in meta.get("counts", {}).get("byType", []))  # type: ignore
    total_count_by_year = sum(item["count"] for item in meta.get("counts", {}).get("byYear", []))  # type: ignore

    # Step 4: Pagination
    current_page = meta.get("page", 1)
    total_pages = meta.get("totalPages", 1)

    if total_pages <= 10:
        page_range = range(1, total_pages + 1)
    else:
        start = max(1, current_page - 5)
        end = min(total_pages, start + 9)
        page_range = range(start, end + 1)

    # Step 5: Modified query links
    modified_query_links = {
        key: urlencode({k: v for k, v in query_params.items() if k != key})
        for key in request.GET.dict()
    }

    # Step 6: Base query string
    query_dict = request.GET.copy()
    query_dict.pop("page", None)
    base_query = urlencode(query_dict)

    # Step 7: Filters
    current_year = str(query_params.get("year", ""))
    current_type = query_params.get("type")
    current_subject = query_params.get("subject")
    subject_heading = current_subject if current_subject and len(current_subject) > 1 else None
    current_subject = current_subject[0] if current_subject else None

    default_pagesize = query_params.get("pageSize", 20)

    # Step 8: Grouping by decade (if applicable)
    grouped_by_decade = False
    if len(meta.get("counts", {}).get("byType", [])) == 1:
        grouped_by_decade = group_by_decade(meta["counts"]["byYear"], current_type)

    # Step 9: Subject initials
    subject_initials = None
    if "bySubjectInitial" in meta.get("counts", {}):
        subject_initials = set(i["initial"] for i in meta["counts"]["bySubjectInitial"])

    # Step 10: Group documents by subject (if filtering by subject)
    grouped_documents = None
    if current_subject:
        grouped_documents = defaultdict(list)
        for doc in documents_data:
            for subject in doc.get("subjects", []):
                grouped_documents[subject].append(doc)
        grouped_documents = dict(grouped_documents)

    # Step 11: Build context
    context: SearchResultContext = {
        "meta_data": meta,
        "documents_data": documents_data,
        "grouped_documents": grouped_documents,
        "page_range": page_range,
        "current_page": current_page,
        "total_pages": total_pages,
        "current_subject": current_subject,
        "subject_heading": subject_heading,
        "total_count_by_type": total_count_by_type,
        "total_count_by_year": total_count_by_year,
        "modified_query_links": modified_query_links,
        "query_params": f"?{base_query}" if base_query else "",
        "query_param": query_params,
        "by_year_pagination_count": len(meta.get("counts", {}).get("byYear", [])),
        "current_year": current_year,
        "current_type": current_type,
        "grouped_by_decade": grouped_by_decade,
        "subject_initials": subject_initials,
        "all_lowercase_letters": string.ascii_lowercase,
        "default_pagesize": default_pagesize,
    }

    return render(request, "new_theme/search_result/search_result.html", context)


def group_by_decade(year_data, doc_type):
    """
    Groups year data into decades with padding for missing years.
    """
    cut_off = get_cutoff(doc_type)
    grouped = defaultdict(dict)

    # Fill in available year data
    for entry in year_data:
        year = entry["year"]
        count = entry["count"]
        complete = year > cut_off

        decade_start = (year // 10) * 10
        decade_label = f"{decade_start}-{decade_start + 9}"

        grouped[decade_label][year] = {
            "year": year,
            "count": count,
            "complete": complete
        }

    # Pad missing years with placeholders
    filled_grouped = {}
    for decade_label, years in grouped.items():
        decade_start = int(decade_label.split("-")[0])
        full_years = []
        for year in range(decade_start, decade_start + 10):
            if year in years:
                full_years.append(years[year])
            else:
                full_years.append({
                    "year": year,
                    "count": 0,
                    "complete": False,
                    "no_data": True
                })
        filled_grouped[decade_label] = full_years

    return dict(sorted(filled_grouped.items()))  # ascending order
