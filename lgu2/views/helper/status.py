
from datetime import date
from typing import List, TypedDict

from django.urls import reverse

from ...api.document import CommonMetadata
from ...api.responses.effects import Effect


class StatusData(TypedDict):
    up_to_date: bool
    label: str
    point_in_time: date
    changes_link: str
    unapplied_effects: 'StatusEffects'


class StatusEffects:
    direct: List[Effect]
    ancestor: List[Effect]


def make_status_data(meta: CommonMetadata) -> StatusData:
    if 'fragment' in meta:
        effects = { 'direct': meta['unappliedEffects']['fragment'], 'ancestor': meta['unappliedEffects']['ancestor'] }
    else:
        effects = { 'direct': meta['unappliedEffects'], 'ancestor': [] }
    return {
        'up_to_date': meta['upToDate'],
        'label': 'this Act',
        'point_in_time': meta['pointInTime'] if meta['pointInTime'] else date.today(),
        'changes_link': reverse('changes-affected', args=[ meta['shortType'], meta['year'], meta['number'] ]),
        'effects': effects
    }
