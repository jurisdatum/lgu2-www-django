from typing import Optional
from urllib.parse import urlencode
from django.urls import reverse, NoReverseMatch
from ..util.types import SEARCH_TYPES
from ..api.search_types import SearchParams

EXTENT_MAP = {
    "E": "england",
    "W": "wales",
    "S": "scotland",
    "NI": "ni",
}
EXTENT_MAP_REVERSE = {v: k for k, v in EXTENT_MAP.items()}


def build_extent_segment(extents: list[str], exclusive: bool = False) -> Optional[str]:
    """
    Convert internal extent codes to browse URL segment.
    Prepends '=' if exclusiveExtent=True
    """
    if not extents:
        return None

    names = [EXTENT_MAP.get(e) for e in extents if EXTENT_MAP.get(e)]
    if not names:
        return None

    segment = "+".join(names)
    if exclusive:
        segment = f"={segment}"
    return segment


def parse_extent_segment(segment: str) -> tuple[list[str], bool]:
    """
    Inverse of build_extent_segment. Returns (extent codes, exclusive flag).
    """
    exclusive = segment.startswith('=')
    if exclusive:
        segment = segment[1:]
    extents = [EXTENT_MAP_REVERSE[s] for s in segment.split('+') if s in EXTENT_MAP_REVERSE]
    return extents, exclusive


def normalize_params_for_browse(params: SearchParams) -> SearchParams:
    """
    Prepares search params for browse URLs.
    Converts startYear/endYear → year string.
    Converts extent list → extent_segment with exclusiveExtent handling.
    """
    browse_params = params.copy()

    # Combine startYear / endYear into a single 'year' param. If year is
    # already set (e.g. a by-year facet link was clicked on a range search),
    # let it win and discard the range.
    start_year = browse_params.pop("startYear", None)
    end_year = browse_params.pop("endYear", None)
    if "year" not in browse_params and (start_year or end_year):
        if start_year and end_year:
            browse_params["year"] = str(start_year) if start_year == end_year else f"{start_year}-{end_year}"
        elif start_year:
            browse_params["year"] = f"{start_year}-*"
        elif end_year:
            browse_params["year"] = f"*-{end_year}"

    # Handle extent list and exclusiveExtent
    extent_list = browse_params.pop("extent", None)
    exclusive = browse_params.pop("exclusiveExtent", False)
    if extent_list:
        extent_segment = build_extent_segment(extent_list, exclusive=exclusive)
        if extent_segment:
            browse_params["extent_segment"] = extent_segment

    return browse_params


def build_browse_url_if_possible(params: SearchParams) -> Optional[str]:
    """
    Build the browse URL if params allow it.
    Handles type(s), year, subject, extent_segment, and exclusiveExtent.
    """
    params = normalize_params_for_browse(params)

    allowed_keys = {
        'type', 'year', 'subject', 'extent_segment',
        'page', 'pageSize', 'title', 'language', 'text', 'number'
    }
    if not set(params).issubset(allowed_keys):
        return None

    tpe = params.get('type')
    if isinstance(tpe, str):
        tpe_list = [tpe]
    elif isinstance(tpe, list):
        tpe_list = tpe
    else:
        return None

    if not all(t in SEARCH_TYPES for t in tpe_list):
        return None

    tpe_url = '+'.join(tpe_list)
    year = params.get("year")
    subject = params.get("subject")
    extent_segment = params.get("extent_segment")
    subject_is_letter = isinstance(subject, str) and len(subject) == 1 and 'a' <= subject <= 'z'

    # path_keys: which params get encoded in the URL path. Remaining params go
    # in the query string (e.g. year under /type/extent stays a query param).
    try:
        if extent_segment:
            base = reverse('browse-extent', kwargs={'type': tpe_url, 'extent_segment': extent_segment})
            path_keys = {'type', 'extent_segment'}
        elif year and subject_is_letter:
            base = reverse('browse-year-subject', kwargs={'type': tpe_url, 'year': year, 'subject': subject})
            path_keys = {'type', 'year', 'subject'}
        elif year:
            base = reverse('browse-year', kwargs={'type': tpe_url, 'year': year})
            path_keys = {'type', 'year'}
        elif subject_is_letter:
            base = reverse('browse-subject', kwargs={'type': tpe_url, 'subject': subject})
            path_keys = {'type', 'subject'}
        else:
            base = reverse('browse', kwargs={'type': tpe_url})
            path_keys = {'type'}
    except NoReverseMatch:
        return None

    query = {k: v for k, v in params.items() if k not in path_keys}
    if query:
        return f"{base}?{urlencode(query, doseq=True)}"
    return base
