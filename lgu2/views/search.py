import string
from urllib.parse import urlencode
from collections import defaultdict
from typing import TypedDict, Optional, List, Dict, Any, Union

from django.shortcuts import render, redirect
from django.urls import reverse

from ..api.search import basic_search
from ..api.search_types import SearchParams
from ..util.cutoff import get_cutoff
from ..util.types import to_short_type
from ..util.version import get_first_version
from ..util.labels import get_type_label
from ..util.links import make_contents_link_for_list_entry
from ..util.global_redirect import build_browse_url_if_possible, normalize_params_for_browse, EXTENT_MAP


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
    current_type: Optional[Union[str, List[str]]]
    grouped_by_decade: bool
    subject_initials: Optional[set[str]]
    subject_initials_and_links: List[Dict[str, Any]]
    subject_heading_links: List[Dict[str, Any]]
    all_lowercase_letters: str
    default_pagesize: int
    type_label_plural: str
    type_made_verb: str


# -------------------------
# Query param helpers
# -------------------------

def parse_year_param(year: str) -> SearchParams:
    if year.isdigit():
        return {"year": int(year)}
    if "-" in year:
        start, end = year.split("-", 1)
        result = {}
        if start.isdigit() and end.isdigit():
            result = {"startYear": int(start), "endYear": int(end)}
        elif start.isdigit() and end == "*":
            result = {"startYear": int(start)}
        elif start == "*" and end.isdigit():
            result = {"endYear": int(end)}
        return result
    return {}


def extract_query_params(request) -> SearchParams:
    params: SearchParams = {}
    mapping = {
        "sort": str,
        "subject": str,
        "title": str,
        "number": str,
        "leg_text": lambda v: ("q", v),
        "language": str,
        "exclusiveExtent": str,
        "pointInTime": str,
        "year": int,
        "startYear": int,
        "endYear": int,
        "page": int,
        "pageSize": int,
        "extent": str
    }

    for key, cast in mapping.items():
        value = request.GET.get(key)
        if value and value.strip():
            if callable(cast):
                if isinstance(cast(value), tuple):
                    k, v = cast(value)
                    params[k] = v
                else:
                    params[key] = cast(value)
            else:
                params[key] = cast(value)

    # Handle types list
    types = [t.strip() for t in request.GET.getlist("type") if t.strip()]
    if types:
        params["type"] = types[0] if len(types) == 1 else types

    # Handle years
    if request.GET.get("specifi_years") == "true" and "year" in request.GET and request.GET["year"].isdigit():
        params["year"] = int(request.GET["year"])
    else:
        if "startYear" in request.GET and request.GET["startYear"].isdigit():
            params["startYear"] = int(request.GET["startYear"])
        if "endYear" in request.GET and request.GET["endYear"].isdigit():
            params["endYear"] = int(request.GET["endYear"])

    # Handle multiple extent values
    extents = request.GET.getlist("extent")
    if extents:
        params["extent"] = extents

    # Normalize exclusiveExtent to boolean
    exclusive = request.GET.get("exclusiveExtent")
    if exclusive is not None:
        params["exclusiveExtent"] = str(exclusive).lower() == "true"

    return params


def make_smart_link(params: SearchParams):
    browse_url = build_browse_url_if_possible(params)
    return browse_url or f"{reverse('search')}?{urlencode(params, doseq=True)}"


def replace_param_and_make_smart_link(params: SearchParams, key: str, value):
    new_params = params.copy()
    new_params[key] = value
    new_params.pop("page", None)
    new_params.pop("pageSize", None)
    return make_smart_link(new_params)


# -------------------------
# Browse / search
# -------------------------

def browse(request, type: str, year: Optional[str] = None, subject: Optional[str] = None, extent_segment: Optional[str] = None):
    params: SearchParams = {'type': type.split('+') if type else []}

    EXTENT_MAP_REVERSE = {v: k for k, v in EXTENT_MAP.items()}

    if extent_segment:
        # Detect exclusiveExtent from '=' prefix
        if extent_segment.startswith('='):
            params['exclusiveExtent'] = True
            extent_segment = extent_segment[1:]  # remove '='
        else:
            params['exclusiveExtent'] = False

        # Convert human-readable extent to internal codes
        extent_codes = [EXTENT_MAP_REVERSE.get(s) for s in extent_segment.split('+') if EXTENT_MAP_REVERSE.get(s)]
        params['extent'] = extent_codes

    if year:
        params.update(parse_year_param(year))
    if subject:
        params['subject'] = subject

    # Copy other GET params
    for key in ['number', 'title', 'leg_text', 'language', 'page', 'pageSize']:
        if key in request.GET and request.GET[key]:
            params[key] = request.GET[key]

    return search_results_helper(request, params)


def search_results(request):
    params = extract_query_params(request)
    browse_params = normalize_params_for_browse(params)
    browse_url = build_browse_url_if_possible(browse_params)
    if browse_url:
        return redirect(browse_url)
    return search_results_helper(request, params)


# -------------------------
# Search results helper
# -------------------------

def search_results_helper(request, query_params: SearchParams):
    current_type = query_params.get("type")
    if isinstance(current_type, list):
        filtered = [t for t in current_type if t != "all"]
        if filtered:
            query_params["type"] = filtered[0] if len(filtered) == 1 else filtered
        else:
            query_params.pop("type", None)
    elif current_type == "all":
        query_params.pop("type", None)

    api_data = basic_search(query_params)
    meta = api_data["meta"]
    documents_data = api_data["documents"]

    total_count_by_type = sum(item["count"] for item in meta.get("counts", {}).get("byType", []))
    total_count_by_year = sum(item["count"] for item in meta.get("counts", {}).get("byYear", []))

    current_page = meta.get("page", 1)
    total_pages = meta.get("totalPages", 1)
    start = max(1, current_page - 5)
    end = min(total_pages, start + 9)
    page_range = range(1, total_pages + 1) if total_pages <= 10 else range(start, end + 1)

    modified_query_links = {k: replace_param_and_make_smart_link(query_params, k, None) for k in query_params.keys()}

    base_query = request.GET.copy()
    base_query.pop("page", None)
    base_query_str = urlencode(base_query)

    current_year = str(query_params.get("year", ""))
    current_type = query_params.get("type")
    single_type = current_type[0] if isinstance(current_type, list) and len(current_type) == 1 else current_type
    current_subject = query_params.get("subject")
    subject_heading = current_subject if current_subject and len(current_subject) > 1 else None
    current_subject = current_subject[0] if current_subject else None
    default_pagesize = query_params.get("pageSize", 20)

    grouped_by_decade = False
    if len(meta.get("counts", {}).get("byType", [])) == 1:
        grouped_by_decade = group_by_decade(meta["counts"]["byYear"], single_type)
        for year_list in grouped_by_decade.values():
            for item in year_list:
                item["link"] = replace_param_and_make_smart_link(query_params, "year", item["year"])

    for byType in meta.get("counts", {}).get("byType", []):
        byType["link"] = replace_param_and_make_smart_link(query_params, "type", to_short_type(byType["type"]))
    for byYear in meta.get("counts", {}).get("byYear", []):
        byYear["link"] = replace_param_and_make_smart_link(query_params, "year", byYear["year"])
    for byInitial in meta.get("counts", {}).get("bySubjectInitial", []):
        byInitial["link"] = replace_param_and_make_smart_link(query_params, "subject", byInitial["initial"])
    for doc in documents_data:
        doc["link"] = make_contents_link_for_list_entry(doc)

    subject_initials = {i["initial"] for i in meta.get("counts", {}).get("bySubjectInitial", [])} or None
    subject_initial_links = {i["initial"]: i["link"] for i in meta.get("counts", {}).get("bySubjectInitial", [])}
    subject_initials_and_links = [
        {"letter": l, "link": subject_initial_links.get(l), "current": (current_subject and current_subject.upper() == l.upper())}
        for l in string.ascii_lowercase
    ]

    subject_heading_links = [
        {"name": h, "link": replace_param_and_make_smart_link(query_params, "subject", h), "current": subject_heading == h}
        for h in meta.get("subjects", [])
    ]

    grouped_documents = None
    if current_subject:
        grouped_documents = defaultdict(list)
        for doc in documents_data:
            for s in doc.get("subjects", []):
                grouped_documents[s].append(doc)
        grouped_documents = dict(grouped_documents)

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
        "query_params": f"?{base_query_str}" if base_query_str else "",
        "query_param": query_params,
        "by_year_pagination_count": len(meta.get("counts", {}).get("byYear", [])),
        "current_year": current_year,
        "current_type": current_type,
        "grouped_by_decade": grouped_by_decade,
        "subject_initials": subject_initials,
        "subject_initials_and_links": subject_initials_and_links,
        "subject_heading_links": subject_heading_links,
        "all_lowercase_letters": string.ascii_lowercase,
        "default_pagesize": default_pagesize,
        "type_label_plural": get_type_label(single_type) if single_type else "documents",
        "type_made_verb": get_first_version(single_type) if single_type else "documents"
    }

    return render(request, "new_theme/search_result/search_result.html", context)


# -------------------------
# Grouping helper
# -------------------------

def group_by_decade(year_data, doc_type):
    cut_off = get_cutoff(doc_type)
    grouped = defaultdict(dict)

    for entry in year_data:
        year = entry["year"]
        count = entry["count"]
        complete = cut_off is not None and year > cut_off
        decade_start = (year // 10) * 10
        decade_label = f"{decade_start}-{decade_start + 9}"
        grouped[decade_label][year] = {"year": year, "count": count, "complete": complete}

    filled_grouped = {}
    for decade_label, years in grouped.items():
        decade_start = int(decade_label.split("-")[0])
        full_years = [
            years.get(y, {"year": y, "count": 0, "complete": False, "no_data": True})
            for y in range(decade_start, decade_start + 10)
        ]
        filled_grouped[decade_label] = full_years

    return dict(sorted(filled_grouped.items()))
