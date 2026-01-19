import re
from ..util.types import VALID_TYPES, EXTENT_MAP
from django.urls import reverse
from urllib.parse import urlencode
from ..api.search_types import SearchParams

TYPE = r'(?P<type>(?:' + '|'.join(VALID_TYPES) + r')(?:\+(?:' + '|'.join(VALID_TYPES) + r'))*)'
PARAM_RENAME = {
    'q': 'text',  # rename q -> text
}


def build_extent_segment(extents: list[str], exclusive: bool = False) -> Optional[str]:
    """
    Convert extent codes to browse segment.
    If exclusiveExtent=True, might filter differently (for now we just map names)
    """
    if not extents:
        return None

    names = [EXTENT_MAP.get(e) for e in extents if EXTENT_MAP.get(e)]
    if not names:
        return None

    # Join with +
    return "+".join(names)


def normalize_params_for_browse(params: SearchParams) -> SearchParams:
    """
    Convert startYear/endYear into a single 'year' string
    ONLY for browse URL generation.
    """
    browse_params = params.copy()

    start_year = browse_params.pop("startYear", None)
    end_year = browse_params.pop("endYear", None)

    if start_year or end_year:
        if start_year and end_year:
            if start_year == end_year:
                browse_params["year"] = str(start_year)
            else:
                browse_params["year"] = f"{start_year}-{end_year}"
        elif start_year:
            browse_params["year"] = f"{start_year}-*"
        elif end_year:
            browse_params["year"] = f"*-{end_year}"

    # Handle extent → subject
    extent_list = browse_params.pop("extent", None)
    exclusive = browse_params.pop("exclusiveExtent", None)
    if extent_list:
        browse_subject = build_extent_segment(extent_list, exclusive=exclusive)
        if browse_subject:
            browse_params["subject"] = browse_subject

    return browse_params


def build_browse_url_if_possible(params: SearchParams) -> Optional[str]:
    """
    Build browse URL if params qualify for clean URL routing, None otherwise.

    Supports multiple types (as list) and enforces validation for type/year/subject/page/pageSize keys.
    """
    
    params = normalize_params_for_browse(params)
    
    allowed_keys = {'type', 'year', 'subject', 'page', 'pageSize', 'title', 'language', 'q', 'number'}
    if not set(params).issubset(allowed_keys):
        return None

    # Normalize type to list
    tpe = params.get('type')
    if isinstance(tpe, str):
        tpe_list = [tpe]
    elif isinstance(tpe, list):
        tpe_list = tpe
    else:
        return None

    # Validate all types: allow 'all' or any type in VALID_TYPES
    if not tpe_list or any(t not in VALID_TYPES for t in tpe_list):
        return None

    # Join types for URL
    tpe_url = '+'.join(tpe_list)

    # Validate year
    year = params.get("year")
    if year:
        if isinstance(year, int):
            year = str(year)
            params["year"] = year

        if not re.match(r'^(\d{4}|\d{4}-\d{4}|\d{4}-\*|\*-\d{4})$', year):
            return None


    # Validate subject
    subject = params.get('subject')
    if subject is not None and not re.match('^[a-z]$', subject):
        return None

    # Build base URL using reverse
    if year:
        if subject:
            base = reverse('browse-year-subject', kwargs={'type': tpe_url, 'year': year, 'subject': subject})
        else:
            base = reverse('browse-year', kwargs={'type': tpe_url, 'year': year})
    else:
        if subject:
            base = reverse('browse-subject', kwargs={'type': tpe_url, 'subject': subject})
        else:
            base = reverse('browse', kwargs={'type': tpe_url})

    # Add optional query params
    # query = {k: params[k] for k in ('page', 'pageSize', 'title', 'text') if k in params}
    # Build query string with remaining params and apply renaming
    query = {}
    for k, v in params.items():
        if k in ('year', 'subject', 'type'):
            continue
        # Rename if needed
        new_key = PARAM_RENAME.get(k, k)
        query[new_key] = v

    if query:
        return f"{base}?{urlencode(query, doseq=True)}"
    return base

