
from datetime import date, datetime
from typing import List, Optional, TypedDict

from django.urls import reverse

from ...api.document import CommonMetadata
from ...api.responses.effects import Effect


class StatusMessage(TypedDict):
    heading: str
    body: str


def make_pdf_status_message(meta: CommonMetadata) -> Optional[StatusMessage]:
    """Return a status message to display alongside a PDF rendering, or None.

    Currently the King's Printer copy is shown only for the enacted version
    of an Act; other document types and revised versions get no message.
    """
    if meta['version'] != 'enacted':
        return None
    return {
        'heading': "This is the King's Printer Version. It is the exact text that received Royal Assent when it was enacted.",
        'body': "A version of this text with commencement and extent information should be available by.",
    }


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
    doc_title = meta['title']
    today = datetime.now().strftime('%d %B %Y')
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
        'message': f'{ doc_title } is up to date with all changes known to be in force on or before { today }.',
        'up_to_date': meta['upToDate'],
        'label': meta['title'],
        'point_in_time': meta['pointInTime'] if meta['pointInTime'] else date.today(),
        'changes_link': reverse('changes-affected', args=[ meta['shortType'], meta['year'], meta['number'] ]),
        'effects': effects
    }
