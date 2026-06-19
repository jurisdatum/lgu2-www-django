import string
from collections import defaultdict
from typing import TypedDict, Optional, List, Dict, Any, Union

from django.shortcuts import render, redirect
from django.urls import reverse

from ..api.search import basic_search
from ..util.cutoff import get_cutoff
from ..util.search_params import SearchParams, from_api_response, to_api_request
from ..util.types import get_category, is_eu_originating_type, to_short_type
from ..util.version import get_first_version
from ..util.labels import get_type_label
from ..util.links import make_contents_link_for_list_entry, make_document_link
from ..util.global_redirect import (
    build_browse_url_if_possible,
    normalize_params_for_browse,
    parse_extent_segment,
)
from ..util.url_params import to_ui_params


class SearchResultContext(TypedDict):
    meta_data: Dict[str, Any]
    documents_data: List[Any]
    grouped_documents: Optional[Dict[str, List[Any]]]
    page_range: range
    current_page: int
    total_pages: int
    current_subject: Optional[str]
    subject_heading: Optional[str]
    modified_query_links: Dict[str, str]
    query_params: str
    query_param: SearchParams
    by_year_pagination_count: int
    current_year: str
    current_type: Optional[Union[str, List[str]]]
    current_stage: Optional[str]
    current_department: Optional[str]
    grouped_by_decade: bool
    subject_initials: Optional[set[str]]
    subject_initials_and_links: List[Dict[str, Any]]
    subject_heading_links: List[Dict[str, Any]]
    all_lowercase_letters: str
    default_pagesize: int
    type_label_plural: str
    type_made_verb: str
    type_filter_groups: List[Dict[str, Any]]
    active_filters: List[Dict[str, Any]]
    query_param_ui: Dict[str, Any]


def enforce_uk_amended_invariant(params: SearchParams) -> SearchParams:
    """Drop ukAmended unless params['type'] contains an EU-originating type.

    Mutates and returns the dict. Compound type sets are EU-positive when
    any member is EU-originating; aggregate tokens 'eu-origin' / 'eu' count.
    """
    if "ukAmended" not in params:
        return params
    type_value = params.get("type")
    if isinstance(type_value, list):
        type_values = type_value
    elif isinstance(type_value, str):
        type_values = [type_value]
    else:
        type_values = []
    if not any(is_eu_originating_type(t) for t in type_values):
        params.pop("ukAmended", None)
    return params


def parse_year_param(year: str) -> SearchParams:
    if _valid_year(year):
        return {"year": int(year)}
    if "-" in year:
        start, end = year.split("-", 1)
        start_ok = _valid_year(start)
        end_ok = _valid_year(end)
        if start_ok and end_ok:
            if int(start) > int(end):
                return {}
            return {"startYear": int(start), "endYear": int(end)}
        if start_ok and end == "*":
            return {"startYear": int(start)}
        if start == "*" and end_ok:
            return {"endYear": int(end)}
    return {}


# TODO: refactor to reduce cyclomatic complexity (currently 22, limit 12)
def extract_query_params(request) -> SearchParams:  # noqa: C901
    params: SearchParams = {}

    for key in (
        "sort",
        "subject",
        "title",
        "number",
        "text",
        "language",
        "pointInTime",
    ):
        value = request.GET.get(key)
        if value and value.strip():
            params[key] = value.strip()

    # Forms submit compound types as a single value with '+' separators
    # (e.g. "primary+secondary" from the header search). Split so downstream
    # code always sees atoms. 'all' is the form's UI value for "no type
    # filter"; the API expects the type parameter omitted entirely in that
    # case.
    types = [
        part.strip()
        for value in request.GET.getlist("type")
        for part in value.split("+")
        if part.strip() and part.strip() != "all"
    ]
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

    if "stage" in request.GET and request.GET["stage"].strip():
        params["stage"] = request.GET["stage"]

    if "department" in request.GET and request.GET["department"]:
        params["department"] = request.GET["department"]

    # ukamended (UI URL spelling, all lowercase) → ukAmended (internal/API).
    # Only literal "true"/"false" (case-insensitive) are accepted; other
    # values are dropped. EU-type invariant is applied later, after path
    # params are merged.
    uk_amended = request.GET.get("ukamended")
    if uk_amended is not None:
        normalized = uk_amended.strip().lower()
        if normalized == "true":
            params["ukAmended"] = True
        elif normalized == "false":
            params["ukAmended"] = False

    return params


def make_smart_link(params: SearchParams):
    """Build a UI URL from already-normalised SearchParams.

    Callers must ensure params already satisfy the EU-type invariant — for
    any link that changes or clears `type`, route through
    `replace_param_and_make_smart_link` which re-applies the invariant.
    """
    browse_url = build_browse_url_if_possible(params)
    if browse_url:
        return browse_url
    ui_params = to_ui_params(params)
    return reverse("search", query=ui_params or None)


def _change_params_and_make_smart_link(
    params: SearchParams, changes: Dict[str, Any]
) -> str:
    """Copy `params`, apply `changes` (None→pop, else set), drop pagination,
    and build a smart link. The EU-type invariant is re-applied only when
    `type` is among the changed keys — other mutations can't affect it.
    """
    new_params = params.copy()
    for key, value in changes.items():
        if value is None:
            new_params.pop(key, None)
        else:
            new_params[key] = value
    new_params.pop("page", None)
    new_params.pop("pageSize", None)
    if "type" in changes:
        enforce_uk_amended_invariant(new_params)
    return make_smart_link(new_params)


def replace_param_and_make_smart_link(params: SearchParams, key: str, value) -> str:
    return _change_params_and_make_smart_link(params, {key: value})


_UK_AMENDED_CHIP_LABELS = {
    True: "Amended by UK legislation",
    False: "Not amended by UK legislation",
}

_UK_AMENDED_SUFFIXES = {
    True: "that are amended by the UK",
    False: "that are not amended by the UK",
}

# Internal SearchParams keys that aren't user-facing filter chips.
_NON_CHIP_KEYS = frozenset({"page", "pageSize", "sort", "exclusiveExtent"})


def _make_type_facet_link(
    query_params: SearchParams, short_type: str, uk_amended
) -> str:
    return _change_params_and_make_smart_link(
        query_params, {"type": short_type, "ukAmended": uk_amended}
    )


def _build_type_filter_groups(by_type_rows, query_params: SearchParams, single_type):
    """Group flat byType API rows by base short_type, producing a view-model
    list with parent + sub_entries (each carrying a `current` flag).

    Sub-entries are sorted Amended → Not amended.
    """
    active_uk_amended = query_params.get("ukAmended")
    has_uk_amended_filter = "ukAmended" in query_params

    groups_by_type: Dict[str, Dict[str, Any]] = {}
    ordered: List[Dict[str, Any]] = []

    for row in by_type_rows:
        short_type = to_short_type(row["type"])
        uk_amended = row.get("ukAmended")
        link = _make_type_facet_link(query_params, short_type, uk_amended)
        is_type_active = single_type == short_type

        group = groups_by_type.get(short_type)
        if group is None:
            group = {
                "base_type": short_type,
                "label": get_type_label(short_type),
                "parent": None,
                "sub_entries": [],
            }
            groups_by_type[short_type] = group
            ordered.append(group)

        if uk_amended is None:
            group["parent"] = {
                "count": row["count"],
                "link": link,
                "current": is_type_active and not has_uk_amended_filter,
            }
        else:
            group["sub_entries"].append(
                {
                    "ukAmended": uk_amended,
                    "label": f"{group['label']} {_UK_AMENDED_SUFFIXES[uk_amended]}",
                    "count": row["count"],
                    "link": link,
                    "current": is_type_active and active_uk_amended is uk_amended,
                }
            )

    for group in ordered:
        group["sub_entries"].sort(key=lambda e: not e["ukAmended"])

    # When a ukAmended filter is active, the API can't return reliable counts
    # for the parent total or the opposite sub-entry — collapse the group to
    # the single matching sub-entry, promoted into the parent slot.
    if has_uk_amended_filter:
        collapsed: List[Dict[str, Any]] = []
        for group in ordered:
            match = next(
                (
                    e
                    for e in group["sub_entries"]
                    if e["ukAmended"] is active_uk_amended
                ),
                None,
            )
            if match is None:
                continue
            group["label"] = match["label"]
            group["parent"] = {
                "count": match["count"],
                "link": match["link"],
                "current": match["current"],
            }
            group["sub_entries"] = []
            collapsed.append(group)
        return collapsed

    # Drop groups whose parent row was missing from the API: Django doesn't
    # synthesise counts (per the ADR), so omit rather than render an empty link.
    return [g for g in ordered if g["parent"] is not None]


_YEAR_RANGE_KEYS = frozenset({"year", "startYear", "endYear"})


def _build_active_filters(
    query_params: SearchParams,
    year_clear_link: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Active-filter chips, built from normalized query_params.

    Each chip carries a friendly label, an optional value, and a removal
    link. For year/startYear/endYear, `year_clear_link` (if provided) is
    used so removing one half of a range escapes the whole filter; without
    it, clearing only one key would leave a half-range in the URL.
    """
    chips: List[Dict[str, Any]] = []
    for key, value in query_params.items():
        if key in _NON_CHIP_KEYS:
            continue
        if key == "ukAmended":
            label = _UK_AMENDED_CHIP_LABELS[value]
            display_value: Any = None
        else:
            label = key
            display_value = value
        if key in _YEAR_RANGE_KEYS and year_clear_link is not None:
            remove_link = year_clear_link
        else:
            remove_link = replace_param_and_make_smart_link(query_params, key, None)
        chips.append(
            {
                "key": key,
                "label": label,
                "value": display_value,
                "remove_link": remove_link,
            }
        )
    return chips


def browse(
    request,
    type: str,
    year: Optional[str] = None,
    subject: Optional[str] = None,
    extent_segment: Optional[str] = None,
):
    # Start from GET params so query-string filters (e.g. ?year=2024 on an
    # extent URL) aren't dropped, then let the URL path override.
    params = extract_query_params(request)
    params["type"] = type.split("+")

    if extent_segment:
        params["extent"], params["exclusiveExtent"] = parse_extent_segment(
            extent_segment
        )

    if year:
        params.pop("year", None)
        params.pop("startYear", None)
        params.pop("endYear", None)
        params.update(parse_year_param(year))
    if subject:
        params["subject"] = subject

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
        value = request.GET.get(field, "").strip()
        if not value:
            continue
        if _valid_year(value):
            continue
        if allow_range and parse_year_param(value):
            continue
        return True

    start = request.GET.get("startYear", "").strip()
    end = request.GET.get("endYear", "").strip()
    if _valid_year(start) and _valid_year(end) and int(start) > int(end):
        return True

    for field in ("page", "pageSize"):
        value = request.GET.get(field, "").strip()
        if value and not value.isdigit():
            return True

    return False


def search_results(request):
    if _has_invalid_params(request):
        return render(request, "new_theme/advance_search/full_search.html")
    params = extract_query_params(request)
    # Apply the EU-type invariant before the redirect check so a
    # /search?type=ukpga&ukamended=true URL canonicalises to /ukpga, never
    # /ukpga?ukamended=true. The helper applies it again redundantly.
    enforce_uk_amended_invariant(params)
    browse_params = normalize_params_for_browse(params)
    browse_url = build_browse_url_if_possible(browse_params)
    if browse_url:
        return redirect(browse_url)
    return search_results_helper(request, params)


# TODO: refactor to reduce cyclomatic complexity (currently 22, limit 12)
def search_results_helper(request, query_params: SearchParams):  # noqa: C901
    query_params = query_params.copy()
    current_type = query_params.get("type")
    if isinstance(current_type, list):
        filtered = [t for t in current_type if t != "all"]
        if filtered:
            query_params["type"] = filtered[0] if len(filtered) == 1 else filtered
        else:
            query_params.pop("type", None)
    elif current_type == "all":
        query_params.pop("type", None)

    # Single normalisation boundary for the EU-type invariant: applied here
    # after path params have been merged into the dict, before API calls,
    # link generation, active-filter construction, or template context.
    enforce_uk_amended_invariant(query_params)

    api_data = from_api_response(basic_search(to_api_request(query_params)))
    meta = api_data["meta"]
    documents_data = api_data["documents"]

    current_page = meta.get("page", 1)
    total_pages = meta.get("totalPages", 1)
    start = max(1, current_page - 5)
    end = min(total_pages, start + 9)
    page_range = (
        range(1, total_pages + 1) if total_pages <= 10 else range(start, end + 1)
    )

    modified_query_links = {
        k: replace_param_and_make_smart_link(query_params, k, None)
        for k in query_params.keys()
    }

    # A year range lands in query_params as startYear/endYear (or one of them),
    # not "year". Compute a single link that clears every year alias so the
    # sidebar's "All years" link and any year chip's remove action fully
    # escape the range — otherwise removing one half would leave the other.
    year_clear_link: Optional[str] = None
    if any(k in query_params for k in _YEAR_RANGE_KEYS):
        clear_year = query_params.copy()
        for field in ("year", "startYear", "endYear", "page", "pageSize"):
            clear_year.pop(field, None)
        year_clear_link = make_smart_link(clear_year)
        for field in _YEAR_RANGE_KEYS:
            modified_query_links[field] = year_clear_link

    base_query = request.GET.copy()
    base_query.pop("page", None)
    base_query_str = base_query.urlencode()

    if "year" in query_params:
        current_year = str(query_params["year"])
    elif "startYear" in query_params or "endYear" in query_params:
        start = query_params.get("startYear")
        end = query_params.get("endYear")
        current_year = (
            f"{start if start is not None else '*'}-{end if end is not None else '*'}"
        )
    else:
        current_year = ""
    current_type = query_params.get("type")
    if isinstance(current_type, list):
        single_type = current_type[0] if len(current_type) == 1 else None
    else:
        single_type = current_type
    current_subject = query_params.get("subject")
    subject_heading = (
        current_subject if current_subject and len(current_subject) > 1 else None
    )
    current_subject = current_subject[0] if current_subject else None
    current_stage = query_params.get("stage")
    current_department = query_params.get("department")

    default_pagesize = query_params.get("pageSize", 20)

    by_type_rows = meta.get("counts", {}).get("byType", [])
    type_filter_groups = _build_type_filter_groups(
        by_type_rows, query_params, single_type
    )
    active_filters = _build_active_filters(query_params, year_clear_link)

    grouped_by_decade = False
    if len(type_filter_groups) == 1:
        grouped_by_decade = group_by_decade(meta["counts"]["byYear"], single_type)
        for year_list in grouped_by_decade.values():
            for item in year_list:
                item["link"] = replace_param_and_make_smart_link(
                    query_params, "year", item["year"]
                )

    for byYear in meta.get("counts", {}).get("byYear", []):
        byYear["link"] = replace_param_and_make_smart_link(
            query_params, "year", byYear["year"]
        )
    for byInitial in meta.get("counts", {}).get("bySubjectInitial", []):
        byInitial["link"] = replace_param_and_make_smart_link(
            query_params, "subject", byInitial["initial"]
        )
    for byStage in meta.get("counts", {}).get("byStage", []):
        byStage["link"] = replace_param_and_make_smart_link(
            query_params, "stage", byStage["stage"]
        )
    for byDepartment in meta.get("counts", {}).get("byDepartment", []):
        byDepartment["link"] = replace_param_and_make_smart_link(
            query_params, "department", byDepartment["department"]
        )
    for doc in documents_data:
        short_type = doc["id"].split("/")[0]
        if get_category(short_type) == "associated":
            doc["link"] = make_document_link(
                short_type, doc["year"], doc["number"], None, None
            )
        else:
            doc["link"] = make_contents_link_for_list_entry(doc)

    subject_initials = {
        i["initial"] for i in meta.get("counts", {}).get("bySubjectInitial", [])
    } or None
    subject_initial_links = {
        i["initial"]: i["link"]
        for i in meta.get("counts", {}).get("bySubjectInitial", [])
    }
    subject_initials_and_links = [
        {
            "letter": letter,
            "link": subject_initial_links.get(letter),
            "current": (current_subject and current_subject.upper() == letter.upper()),
        }
        for letter in string.ascii_lowercase
    ]

    subject_heading_links = [
        {
            "name": h,
            "link": replace_param_and_make_smart_link(query_params, "subject", h),
            "current": subject_heading == h,
        }
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
        "modified_query_links": modified_query_links,
        "query_params": f"?{base_query_str}" if base_query_str else "",
        "query_param": query_params,
        "by_year_pagination_count": len(meta.get("counts", {}).get("byYear", [])),
        "current_year": current_year,
        "current_type": current_type,
        "current_stage": current_stage,
        "current_department": current_department,
        "grouped_by_decade": grouped_by_decade,
        "subject_initials": subject_initials,
        "subject_initials_and_links": subject_initials_and_links,
        "subject_heading_links": subject_heading_links,
        "all_lowercase_letters": string.ascii_lowercase,
        "default_pagesize": default_pagesize,
        "type_label_plural": (
            get_type_label(single_type) if single_type else "documents"
        ),
        "type_made_verb": (
            get_first_version(single_type) if single_type else "documents"
        ),
        "type_filter_groups": type_filter_groups,
        "active_filters": active_filters,
        "query_param_ui": to_ui_params(query_params),
    }

    return render(request, "new_theme/search_result/search_result.html", context)


def group_by_decade(year_data, doc_type):
    cut_off = get_cutoff(doc_type)
    grouped = defaultdict(dict)

    for entry in year_data:
        year = entry["year"]
        count = entry["count"]
        complete = cut_off is not None and year >= cut_off
        decade_start = (year // 10) * 10
        decade_label = f"{decade_start}-{decade_start + 9}"
        grouped[decade_label][year] = {
            "year": year,
            "count": count,
            "complete": complete,
        }

    filled_grouped = {}
    for decade_label, years in grouped.items():
        decade_start = int(decade_label.split("-")[0])
        full_years = [
            years.get(y, {"year": y, "count": 0, "complete": False, "no_data": True})
            for y in range(decade_start, decade_start + 10)
        ]
        filled_grouped[decade_label] = full_years

    return dict(sorted(filled_grouped.items()))
