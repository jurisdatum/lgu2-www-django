import re
from typing import Optional
from urllib.parse import urlencode
from django.urls import reverse
from ..util.types import VALID_TYPES, EXTENT_MAP
from ..api.search_types import SearchParams

# Regex to match type(s) in URL
TYPE = r'(?P<type>(?:' + '|'.join(VALID_TYPES) + r')(?:\+(?:' + '|'.join(VALID_TYPES) + r'))*)'

# Param renames for query string
PARAM_RENAME = {
    'q': 'text',
}


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
        segment = f"={segment}"  # prepend '=' for exclusive
    return segment


def normalize_params_for_browse(params: SearchParams) -> SearchParams:
    """
    Prepares search params for browse URLs.
    Converts startYear/endYear → year string.
    Converts extent list → extent_segment with exclusiveExtent handling.
    """
    browse_params = params.copy()

    # Combine startYear / endYear into a single 'year' param
    start_year = browse_params.pop("startYear", None)
    end_year = browse_params.pop("endYear", None)
    if start_year or end_year:
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

    allowed_keys = {'type', 'year', 'subject', 'extent_segment', 'page', 'pageSize', 'title', 'language', 'q', 'number'}
    if not set(params).issubset(allowed_keys):
        return None

    # Prepare type(s) string
    tpe = params.get('type')
    if isinstance(tpe, str):
        tpe_list = [tpe]
    elif isinstance(tpe, list):
        tpe_list = tpe
    else:
        return None
    tpe_url = '+'.join(tpe_list)

    year = params.get("year")
    subject = params.get("subject")
    extent_segment = params.get("extent_segment")

    # Determine URL pattern
    if extent_segment:
        base = reverse('browse-extent', kwargs={'type': tpe_url, 'extent_segment': extent_segment})
    elif year:
        if subject:
            base = reverse('browse-year-subject', kwargs={'type': tpe_url, 'year': year, 'subject': subject})
        else:
            base = reverse('browse-year', kwargs={'type': tpe_url, 'year': year})
    else:
        if subject:
            base = reverse('browse-subject', kwargs={'type': tpe_url, 'subject': subject})
        else:
            base = reverse('browse', kwargs={'type': tpe_url})

    # Add remaining query params (page, pageSize, title, text, number)
    query = {}
    for k, v in params.items():
        if k in ('year', 'subject', 'type', 'extent_segment'):
            continue
        new_key = PARAM_RENAME.get(k, k)
        query[new_key] = v

    if query:
        return f"{base}?{urlencode(query, doseq=True)}"
    return base
