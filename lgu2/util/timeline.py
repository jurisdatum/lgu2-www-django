from datetime import date
import re
from typing import List, Optional, TypedDict, Callable, Union
from django.urls import reverse

from lgu2.api.document import CommonMetadata, DocumentMetadata
from lgu2.api.fragment import FragmentMetadata


class TimelineEntry(TypedDict):
    label: str
    date: Optional[date]
    link: Optional[str]


class TimelineData(TypedDict):
    original: Optional[TimelineEntry]
    current: Optional[TimelineEntry]
    historical: List[TimelineEntry]
    viewing: TimelineEntry
    pointInTime: Optional[date]


_ISO_DATE_RE = re.compile(r'\d{4}-\d{2}-\d{2}')


def make_timeline_data(
    meta: Union[DocumentMetadata, FragmentMetadata, CommonMetadata],
    target: str,  # 'document', 'fragment', or 'toc'
    lang: Optional[str] = None,
) -> TimelineData:
    """
    Generic function to build timeline data for documents, fragments, or TOCs.

    Refactoring justification:
    - Removes near-identical code repeated across three functions.
    - Makes adding new targets (e.g. 'appendix') trivial.
    - Centralizes URL logic for maintainability.
    """

    def make_link(version: Optional[str]) -> str:
        year: Union[int, str] = meta['regnalYear'] if 'regnalYear' in meta else meta['year']

        args = [meta['shortType'], year, meta['number']]

        # Fragment timelines include the fragment href before optional version/lang args
        if target == 'fragment':
            args.append(meta['fragmentInfo']['href'])

        # Build route name dynamically
        suffix = ""
        if version:
            suffix += "-version"
        if lang:
            suffix += "-lang"
        route_name = f"{target}{suffix}"

        # Append version if needed
        if version:
            args.append(version)
        if lang:
            args.append(lang)

        return reverse(route_name, args=args)

    return _make_timeline_data(meta, make_link)


def _make_timeline_data(meta: CommonMetadata, make_link: Callable) -> TimelineData:
    versions = meta['versions'].copy()
    point_in_time = meta.get("pointInTime")

    original = None
    if versions and not _ISO_DATE_RE.fullmatch(versions[0]) and versions[0] != 'prospective':
        version = versions.pop(0)
        original = {
            'label': version,
            'date': meta.get('date'),
            'link': make_link(version),
        }

    current = None
    if versions:
        version = versions.pop(-1)
        current = {
            'label': version,
            'date': None if version == 'prospective' else date.fromisoformat(version),
            'link': make_link(None),
        }

    historical = [
        {'label': v, 'date': date.fromisoformat(v), 'link': make_link(v)}
        for v in versions
    ]

    viewing = None
    if original and original['label'] == meta['version']:
        viewing = original
    elif current and current['label'] == meta['version']:
        viewing = current
    else:
        viewing = next(v for v in historical if v['label'] == meta['version'])

    
    # NEW: detect single-version timeline
    version_count = (
        (1 if original else 0)
        + len(historical)
        + (1 if current else 0)
    )

    return {
        'original': original,
        'historical': historical,
        'current': current,
        'viewing': viewing,
        'pointInTime': point_in_time,
        'single_version': version_count == 1,  # ✅
    }
