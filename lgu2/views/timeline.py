
from datetime import date
import re
from typing import List, Optional, TypedDict

from django.urls import reverse

from lgu2.api.document import CommonMetadata, DocumentMetadata
from lgu2.api.fragment import FragmentMetadata


class TimelineEntry(TypedDict):
    label: str
    date: Optional[date]
    link: Optional[str]


class TimelineData(TypedDict):
    original: Optional[TimelineEntry]
    current:  Optional[TimelineEntry]
    historical: List[TimelineEntry]
    viewing: TimelineEntry


_ISO_DATE_RE = re.compile(r'\d{4}-\d{2}-\d{2}')


def make_timeline_data_for_document(meta: DocumentMetadata) -> TimelineData:
    def make_link(version: Optional[str]):
        if version:
            return reverse('document-version', args=[ meta['shortType'], meta['year'], meta['number'], version ])
        else:
            return reverse('document', args=[ meta['shortType'], meta['year'], meta['number'] ])
    return _make_timeline_data(meta, make_link)


def make_timeline_data_for_fragment(meta: FragmentMetadata) -> TimelineData:
    def make_link(version: Optional[str]):
        if version:
            return reverse('fragment-version', args=[ meta['shortType'], meta['year'], meta['number'], meta['fragmentInfo']['href'], version ])
        else:
            return reverse('fragment', args=[ meta['shortType'], meta['year'], meta['number'], meta['fragmentInfo']['href'] ])
    return _make_timeline_data(meta, make_link)


def make_timeline_data_for_toc(meta: CommonMetadata) -> TimelineData:
    def make_link(version: Optional[str]):
        if version:
            return reverse('toc-version', args=[ meta['shortType'], meta['year'], meta['number'], version ])
        else:
            return reverse('toc', args=[ meta['shortType'], meta['year'], meta['number'] ])
    return _make_timeline_data(meta, make_link)


def _make_timeline_data(meta: CommonMetadata, make_link) -> TimelineData:

    versions = meta['versions'].copy()
    original = None

    # pointInTime is already converted to date object by API layer
    point_in_time = meta.get("pointInTime")

    if versions and not _ISO_DATE_RE.fullmatch(versions[0]) and 'prospective' != versions[0]:
        version = versions.pop(0)
        original = {
            'label': version,
            'date': meta['date'],
            'link': make_link(version)
        }
    current = None
    if versions:
        version = versions.pop(-1)
        if version == 'prospective':
            current = {
                'label': version,
                'date': None,
                'link': make_link(None)
            }
        else:
            current = {
                'label': version,
                'date': date.fromisoformat(version),
                'link': make_link(None)
            }
    historical = [ {
            'label': version,
            'date': date.fromisoformat(version),
            'link': make_link(version)
        } for version in versions ]
    viewing = None
    if original and original['label'] == meta['version']:
        viewing = original
    elif current and current['label'] == meta['version']:
        viewing = current
    else:
        viewing = next(v for v in historical if v['label'] == meta['version'])
    return {
        'original': original,
        'historical': historical,
        'current': current,
        'viewing': viewing,
        'pointInTime': point_in_time
    }
