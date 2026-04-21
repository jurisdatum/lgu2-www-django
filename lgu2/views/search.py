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
from ..util.global_redirect import build_browse_url_if_possible, normalize_params_for_browse, parse_extent_segment


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


def parse_year_param(year: str) -> SearchParams:
    if _valid_year(year):
        return {"year": int(year)}
    if "-" in year:
        start, end = year.split("-", 1)
        start_ok = _valid_year(start)
        end_ok = _valid_year(end)
        if start_ok and end_ok:
            return {"startYear": int(start), "endYear": int(end)}
        if start_ok and end == "*":
            return {"startYear": int(start)}
        if start == "*" and end_ok:
            return {"endYear": int(end)}
    return {}


def extract_query_params(request) -> SearchParams:
    params: SearchParams = {}

    for key in ("sort", "subject", "title", "number", "text", "language", "pointInTime"):
        value = request.GET.get(key)
        if value and value.strip():
            params[key] = value

    types = [t.strip() for t in request.GET.getlist("type") if t.strip()]
    if types:
        params["type"] = types[0] if len(types) == 1 else types

    # Handle years. The radio button tells us specific vs range mode when the
    # user submits the advanced form. Hidden year fields on results pages can
    # arrive without the radio, so treat an absent radio as "parse year if
    # present, otherwise fall back to range".
    specifi_years = request.GET.get("specifi_years")
    if specifi_years == "true":
        if _valid_year(request.GET.get("year")):
            params["year"] = int(request.GET["year"])
    elif specifi_years == "false":
        if _valid_year(request.GET.get("startYear")):
            params["startYear"] = int(request.GET["startYear"])
        if _valid_year(request.GET.get("endYear")):
            params["endYear"] = int(request.GET["endYear"])
    else:
        year_value = (request.GET.get("year") or "").strip()
        if "-" in year_value:
            # Extent redirects collapse startYear/endYear into year=YYYY-YYYY
            # on the URL; split it back out here.
            params.update(parse_year_param(year_value))
        elif _valid_year(year_value):
            params["year"] = int(year_value)
        else:
            if _valid_year(request.GET.get("startYear")):
                params["startYear"] = int(request.GET["startYear"])
            if _valid_year(request.GET.get("endYear")):
                params["endYear"] = int(request.GET["endYear"])

    # Handle page and pageSize safely
    for key in ("page", "pageSize"):
        value = request.GET.get(key)
        if value and value.strip().isdigit():
            params[key] = int(value)

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
    if value is None:
        new_params.pop(key, None)
    else:
        new_params[key] = value

    new_params.pop("page", None)
    new_params.pop("pageSize", None)
    return make_smart_link(new_params)


def browse(request, type: str, year: Optional[str] = None, subject: Optional[str] = None, extent_segment: Optional[str] = None):
    # Start from GET params so query-string filters (e.g. ?year=2024 on an
    # extent URL) aren't dropped, then let the URL path override.
    params = extract_query_params(request)
    params['type'] = type.split('+') if type else []

    if extent_segment:
        params['extent'], params['exclusiveExtent'] = parse_extent_segment(extent_segment)

    if year:
        params.pop('year', None)
        params.pop('startYear', None)
        params.pop('endYear', None)
        params.update(parse_year_param(year))
    if subject:
        params['subject'] = subject

    return search_results_helper(request, params)


def _valid_year(value) -> bool:
    if not value:
        return False
    value = value.strip()
    return value.isdigit() and 1000 <= int(value) <= 9999


def _has_invalid_params(request) -> bool:
    specifi_years = request.GET.get("specifi_years")
    if specifi_years == "true":
        year_fields = ("year",)
        allow_range = False
    elif specifi_years == "false":
        year_fields = ("startYear", "endYear")
        allow_range = False
    elif request.GET.get("year"):
        year_fields = ("year",)
        allow_range = True  # extent redirects collapse range into year=YYYY-YYYY
    else:
        year_fields = ("startYear", "endYear")
        allow_range = False

    for field in year_fields:
        value = request.GET.get(field, '').strip()
        if not value:
            continue
        if _valid_year(value):
            continue
        if allow_range and parse_year_param(value):
            continue
        return True

    for field in ("page", "pageSize"):
        value = request.GET.get(field, '').strip()
        if value and not value.isdigit():
            return True

    return False


def search_results(request):
    if _has_invalid_params(request):
        return render(request, 'new_theme/advance_search/full_search.html')
    params = extract_query_params(request)
    browse_params = normalize_params_for_browse(params)
    browse_url = build_browse_url_if_possible(browse_params)
    if browse_url:
        return redirect(browse_url)
    return search_results_helper(request, params)


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

    # Rename text→q only for API call, never mutate query_params
    api_params = query_params.copy()
    if "text" in api_params:
        api_params["q"] = api_params.pop("text")

    api_data = basic_search(api_params)
    meta = api_data["meta"]
    # Template renders active-filter chips from meta.query; keep keys aligned
    # with query_params (and modified_query_links) so removal links resolve.
    if "q" in meta.get("query", {}):
        meta["query"]["text"] = meta["query"].pop("q")
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
    if isinstance(current_type, list):
        single_type = current_type[0] if len(current_type) == 1 else None
    else:
        single_type = current_type
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
