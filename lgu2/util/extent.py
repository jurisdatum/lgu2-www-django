
from typing import List

EXTENT_LABELS = {
    'E': 'England',
    'W': 'Wales',
    'S': 'Scotland',
    'NI': 'Northern Ireland'
}

def make_combined_extent_label(extents: List[str]):
    labels = [ EXTENT_LABELS[e] for e in extents ]
    if not labels:
        return ''
    if len(labels) == 1:
        return labels[0]
    return ', '.join(labels[:-1]) + ' and ' + labels[-1]
