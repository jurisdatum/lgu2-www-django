
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


def group_effects(effects):
    grouped = {
        'outstanding': [],
        'prospective': [],
        'fixedFuture': [],
        'unrequired': []
    }
    for effect in effects:
        if effect['outstanding']:
            grouped['outstanding'].append(effect)
        elif not effect['required']:
            grouped['unrequired'].append(effect)
        elif all(ifd['date'] is None for ifd in effect['inForce']):
            grouped['prospective'].append(effect)
        else:
            grouped['fixedFuture'].append(effect)
    return grouped


def make_status_data(meta: CommonMetadata) -> StatusData:
    print(meta)
    if meta['upToDate'] is None:
        effects = None
    elif 'fragment' in meta:
        effects = {
            'direct': group_effects(meta['unappliedEffects']['fragment']),
            'ancestor': group_effects(meta['unappliedEffects']['ancestor'])
        }
    else:
        effects = {
            'direct': group_effects(meta['unappliedEffects']),
            'ancestor': group_effects([])
        }
    return {
        'up_to_date': meta['upToDate'],
        'label': 'this Act',
        'point_in_time': meta['pointInTime'] if meta['pointInTime'] else date.today(),
        'changes_link': reverse('changes-affected', args=[ meta['shortType'], meta['year'], meta['number'] ]),
        'effects': effects
    }
