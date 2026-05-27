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
    entries: List[TimelineEntry]
    current: TimelineEntry
    viewing: TimelineEntry
    pointInTime: Optional[date]
    single_version: bool


_ISO_DATE_RE = re.compile(r'\d{4}-\d{2}-\d{2}')


def make_timeline_data(
    meta: Union[DocumentMetadata, FragmentMetadata, CommonMetadata],
    target: str,  # 'document' or 'fragment'
    lang: Optional[str] = None,
) -> Optional[TimelineData]:

    def make_link(version: Optional[str]) -> str:
        year: Union[int, str] = meta['regnalYear'] if 'regnalYear' in meta else meta['year']

        args = [meta['shortType'], year, meta['number']]

        if target == 'fragment':
            args.append(meta['fragmentInfo']['href'])

        suffix = ""
        if version:
            suffix += "-version"
        if lang:
            suffix += "-lang"
        route_name = f"{target}{suffix}"

        if version:
            args.append(version)
        if lang:
            args.append(lang)

        return reverse(route_name, args=args)

    return _make_timeline_data(meta, make_link)


def _make_timeline_data(meta: CommonMetadata, make_link: Callable) -> Optional[TimelineData]:
    versions = meta['versions'].copy()
    point_in_time = meta.get("pointInTime")

    held_aside = None
    if versions and not _ISO_DATE_RE.fullmatch(versions[0]) and versions[0] != 'prospective':
        label = versions.pop(0)
        held_aside = {
            'label': label,
            'date': meta.get('date'),
        }

    if not versions:
        current = {
            'label': held_aside['label'],
            'date': held_aside['date'],
            'link': make_link(None),
        }
        return {
            'entries': [],
            'current': current,
            'viewing': current,
            'pointInTime': point_in_time,
            'single_version': True,
        }

    if held_aside and held_aside['label'] == meta['version']:
        return None

    current_label = versions.pop(-1)
    current = {
        'label': current_label,
        'date': None if current_label == 'prospective' else date.fromisoformat(current_label),
        'link': make_link(None),
    }

    entries = [
        {'label': v, 'date': date.fromisoformat(v), 'link': make_link(v)}
        for v in versions
    ]

    if current['label'] == meta['version']:
        viewing = current
    else:
        viewing = next(v for v in entries if v['label'] == meta['version'])

    return {
        'entries': entries,
        'current': current,
        'viewing': viewing,
        'pointInTime': point_in_time,
        'single_version': len(entries) == 0,
    }
