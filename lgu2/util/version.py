
from .types import get_category

_first = {'enacted', 'made', 'created', 'adopted'}

def is_first_version(version):
    return version in _first


def get_first_version(type):
    if type == 'ukmo' or type == 'ukci' or type == 'UnitedKingdomMinisterialOrder' or type == 'UnitedKingdomChurchInstrument':
        return 'created'
    cat = get_category(type)
    if cat is None:
        return 'made'
    if cat == 'primary':
        return 'enacted'
    if cat == 'secondary':
        return 'made'
    if cat == 'euretained':
        return 'adopted'
    return 'made'
