
from datetime import date
import re
from typing import List, Optional, TypedDict

from django.urls import reverse

from lgu2.api.document import CommonMetadata


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

def make_timeline_data(meta: CommonMetadata) -> TimelineData:
    versions = meta['versions'].copy()
    original = None

    # pointInTime is already converted to date object by API layer
    point_in_time = meta.get("pointInTime")

    if versions and not _ISO_DATE_RE.fullmatch(versions[0]):
        version = versions.pop(0)
        original = {
            'label': version,
            'date': meta['date'],
            'link': reverse('toc-version', args=[ meta['shortType'], meta['year'], meta['number'], version ])
        }
    current = None
    if versions:
        version = versions.pop(-1)
        current = {
            'label': version,
            'date': date.fromisoformat(version),
            'link': reverse('toc', args=[ meta['shortType'], meta['year'], meta['number'] ])
        }
    historical = [ {
            'label': version,
            'date': date.fromisoformat(version),
            'link': reverse('toc-version', args=[ meta['shortType'], meta['year'], meta['number'], version ])
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
