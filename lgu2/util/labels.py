
# from django.utils.translation import gettext as _

from .types import short_to_long

labels = {
    'ukpga': 'UK Public General Acts',
    'ukla': 'UK Local Acts',
    'ukppa': 'UK Private and Personal Acts',
    'asp': 'Acts of the Scottish Parliament',
    'nia': 'Acts of the Northern Ireland Assembly',
    'aosp': 'Acts of the Old Scottish Parliament',
    'aep': 'Acts of the English Parliament',
    'aip': 'Acts of the Old Irish Parliament',
    'apgb': 'Acts of the Parliament of Great Britain',
    'gbla': 'Local Acts of the Parliament of Great Britain',
    'gbppa': '???',  # ToDo
    'anaw': 'Acts of the National Assembly for Wales',
    'asc': 'Acts of Senedd Cymru',
    'mwa': 'Measures of the National Assembly for Wales',
    'ukcm': 'Church Measures',
    'mnia': 'Measures of the Northern Ireland Assembly',
    'apni': 'Acts of the Northern Ireland Parliament',
    'uksi': 'UK Statutory Instruments',
    'ukmd': 'UK Ministerial Directions',
    'ukmo': 'UK Ministerial Orders',
    'uksro': 'UK Statutory Rules and Orders',
    'wsi': 'Wales Statutory Instruments',
    'ssi': 'Scottish Statutory Instruments',
    'nisi': 'Northern Ireland Orders in Council',
    'nisr': 'Northern Ireland Statutory Rules',
    'ukci': 'Church Instruments',
    'nisro': 'Northern Ireland Statutory Rules and Orders',

    'ukdsi': 'UK Draft Statutory Instruments',
    'sdsi': 'Scottish Draft Statutory Instruments',
    'nidsr': 'Northern Ireland Draft Statutory Rules',

    'eur': 'Regulations originating from the EU',
    'eudn': 'Decisions originating from the EU',
    'eudr': 'Directives originating from the EU'
}
long_labels = labels.copy()
long_labels['uksro'] = 'UK Statutory Rules and Orders 1900-1948'
long_labels['aosp'] = 'Acts of the Old Scottish Parliament 1424-1707'
long_labels['aep'] = 'Acts of the English Parliament 1267-1706'
long_labels['aip'] = 'Acts of the Old Irish Parliament 1495-1800'
long_labels['apgb'] = 'Acts of the Parliament of Great Britain 1707-1800'
long_labels['gbla'] = 'Local Acts of the Parliament of Great Britain 1797-1800'
long_labels['gbppa'] = 'Private and Personal Acts of the Parliament of ' \
    'Great Britain 1707-1800'
long_labels['ukcm'] = 'Church Measures'
long_labels['mnia'] = 'Northern Ireland Assembly Measures 1974'
long_labels['apni'] = 'Acts of the Northern Ireland Parliament 1921-1972'
long_labels['nisro'] = 'Northern Ireland Statutory Rules and Orders 1922-1973'

for short, long in short_to_long.items():
    labels[long] = labels[short]
    long_labels[long] = long_labels[short]


def get_type_label(type):
    if type in labels:
        return labels[type]


def get_long_type_label(type):
    if type in long_labels:
        return long_labels[type]
