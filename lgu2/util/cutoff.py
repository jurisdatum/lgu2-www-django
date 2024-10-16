
from typing import Optional

cutoffs = {
    'ukpga': 1988,
    'ukla': 1991,
    'ukppa': 1946,
    'asp': 1999,
    'nia': 2000,
    'aosp': None,
    'aep': None,
    'aip': None,
    'apgb': None,
    'gbla': None,
    'gbppa': None,
    'anaw': 2012,
    'asc': 2020,
    'mwa': 2008,
    'ukcm': 1988,
    'mnia': None,
    'apni': None,
    'uksi': 1987,
    'ukmd': None,
    'ukmo': None,
    'uksro': None,
    'wsi': 1999,
    'ssi': 1999,
    'nisi': 1987,
    'nisr': 1996,
    'ukci': 1991,
    'nisro': None,
    'ukdsi': 1998,
    'sdsi': 2001,
    'nidsr': 2000,
    'eur': None,
    'eudn': None,
    'eudr': None
}


def get_cutoff(type: str) -> Optional[int]:
    if type in cutoffs:
        return cutoffs[type]
