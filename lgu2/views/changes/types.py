from datetime import datetime

from lgu2.util.labels import labels

TYPES_CODES = [
    'ukpga', 'ukla', 'apgb', 'aep', 'aosp', 'asp', 'aip', 'apni',
    'mnia', 'nia', 'ukcm', 'asc', 'anaw', 'mwa',
    'uksi', 'ssi', 'wsi', 'nisr', 'nisi', 'nisro',
    'eur', 'eudn', 'eudr',
]

TYPES = {code: labels[code]['plural'] for code in TYPES_CODES}

AFFECTING_YEARS = range(2002, datetime.now().year + 1)
