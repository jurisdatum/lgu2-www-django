
# from django.utils.translation import gettext as _

from .types import short_to_long

labels = {
    'ukia':{
        'singular':    'UK impact assessment',
        'plural':      'UK impact assessments',
        'long_plural': 'UK impact assessments',
    },
    'ukpga': {
        'singular':    'UK Public General Act',
        'plural':      'UK Public General Acts',
        'long_plural': 'UK Public General Acts',
    },
    'ukla': {
        'singular':    'UK Local Act',
        'plural':      'UK Local Acts',
        'long_plural': 'UK Local Acts',
    },
    'ukppa': {
        'singular':    'UK Private and Personal Act',
        'plural':      'UK Private and Personal Acts',
        'long_plural': 'UK Private and Personal Acts',
    },
    'asp': {
        'singular':    'Act of the Scottish Parliament',
        'plural':      'Acts of the Scottish Parliament',
        'long_plural': 'Acts of the Scottish Parliament',
    },
    'nia': {
        'singular':    'Act of the Northern Ireland Assembly',
        'plural':      'Acts of the Northern Ireland Assembly',
        'long_plural': 'Acts of the Northern Ireland Assembly',
    },
    'aosp': {
        'singular':    'Act of the Old Scottish Parliament',
        'plural':      'Acts of the Old Scottish Parliament',
        'long_plural': 'Acts of the Old Scottish Parliament 1424-1707',
    },
    'aep': {
        'singular':    'Act of the English Parliament',
        'plural':      'Acts of the English Parliament',
        'long_plural': 'Acts of the English Parliament 1267-1706',
    },
    'aip': {
        'singular':    'Act of the Old Irish Parliament',
        'plural':      'Acts of the Old Irish Parliament',
        'long_plural': 'Acts of the Old Irish Parliament 1495-1800',
    },
    'apgb': {
        'singular':    'Act of the Parliament of Great Britain',
        'plural':      'Acts of the Parliament of Great Britain',
        'long_plural': 'Acts of the Parliament of Great Britain 1707-1800',
    },
    'gbla': {
        'singular':    'Local Act of the Parliament of Great Britain',
        'plural':      'Local Acts of the Parliament of Great Britain',
        'long_plural': 'Local Acts of the Parliament of Great Britain 1797-1800',
    },
    'gbppa': {
        'singular':    'Private and Personal Act of the Parliament of Great Britain',
        'plural':      'Private and Personal Acts of the Parliament of Great Britain',
        'long_plural': 'Private and Personal Acts of the Parliament of Great Britain 1707-1800',
    },
    'anaw': {
        'singular':    'Act of the National Assembly for Wales',
        'plural':      'Acts of the National Assembly for Wales',
        'long_plural': 'Acts of the National Assembly for Wales',
    },
    'asc': {
        'singular':    'Act of Senedd Cymru',
        'plural':      'Acts of Senedd Cymru',
        'long_plural': 'Acts of Senedd Cymru',
    },
    'mwa': {
        'singular':    'Measure of the National Assembly for Wales',
        'plural':      'Measures of the National Assembly for Wales',
        'long_plural': 'Measures of the National Assembly for Wales',
    },
    'ukcm': {
        'singular':    'Church Measure',
        'plural':      'Church Measures',
        'long_plural': 'Church Measures',
    },
    'mnia': {
        'singular':    'Northern Ireland Assembly Measures',
        'plural':      'Measures of the Northern Ireland Assembly',
        'long_plural': 'Measures of the Northern Ireland Assembly 1974',
    },
    'apni': {
        'singular':    'Act of the Northern Ireland Parliament',
        'plural':      'Acts of the Northern Ireland Parliament',
        'long_plural': 'Acts of the Northern Ireland Parliament 1921-1972',
    },
    'uksi': {
        'singular':    'UK Statutory Instrument',
        'plural':      'UK Statutory Instruments',
        'long_plural': 'UK Statutory Instruments',
    },
    'ukmd': {
        'singular':    'UK Ministerial Direction',
        'plural':      'UK Ministerial Directions',
        'long_plural': 'UK Ministerial Directions',
    },
    'ukmo': {
        'singular':    'UK Ministerial Order',
        'plural':      'UK Ministerial Orders',
        'long_plural': 'UK Ministerial Orders',
    },
    'uksro': {
        'singular':    'UK Statutory Rule and Order',
        'plural':      'UK Statutory Rules and Orders',
        'long_plural': 'UK Statutory Rules and Orders 1900-1948',
    },
    'wsi': {
        'singular':    'Wales Statutory Instrument',
        'plural':      'Wales Statutory Instruments',
        'long_plural': 'Wales Statutory Instruments',
    },
    'ssi': {
        'singular':    'Scottish Statutory Instrument',
        'plural':      'Scottish Statutory Instruments',
        'long_plural': 'Scottish Statutory Instruments',
    },
    'nisi': {
        'singular':    'Northern Ireland Order in Council',
        'plural':      'Northern Ireland Orders in Council',
        'long_plural': 'Northern Ireland Orders in Council',
    },
    'nisr': {
        'singular':    'Northern Ireland Statutory Rule',
        'plural':      'Northern Ireland Statutory Rules',
        'long_plural': 'Northern Ireland Statutory Rules',
    },
    'ukci': {
        'singular':    'Church Instrument',
        'plural':      'Church Instruments',
        'long_plural': 'Church Instruments',
    },
    'nisro': {
        'singular':    'Northern Ireland Statutory Rule and Order',
        'plural':      'Northern Ireland Statutory Rules and Orders',
        'long_plural': 'Northern Ireland Statutory Rules and Orders 1922-1973',
    },
    'ukdsi': {
        'singular':    'UK Draft Statutory Instrument',
        'plural':      'UK Draft Statutory Instruments',
        'long_plural': 'UK Draft Statutory Instruments',
    },
    'sdsi': {
        'singular':    'Scottish Draft Statutory Instrument',
        'plural':      'Scottish Draft Statutory Instruments',
        'long_plural': 'Scottish Draft Statutory Instruments',
    },
    'nidsr': {
        'singular':    'Northern Ireland Draft Statutory Rule',
        'plural':      'Northern Ireland Draft Statutory Rules',
        'long_plural': 'Northern Ireland Draft Statutory Rules',
    },
    'eur': {
        'singular':    'EU Regulation',
        'plural':      'Regulations originating from the EU',
        'long_plural': 'Regulations originating from the EU',
    },
    'eudn': {
        'singular':    'EU Decision',
        'plural':      'Decisions originating from the EU',
        'long_plural': 'Decisions originating from the EU',
    },
    'eudr': {
        'singular':    'EU Directive',
        'plural':      'Directives originating from the EU',
        'long_plural': 'Directives originating from the EU',
    },
    'eut': {
        'singular':    'EU Treaty',
        'plural':      'European Union Treaties',
        'long_plural': 'European Union Treaties'
    }
}

for short, long in short_to_long.items():
    labels[long] = labels[short]


def get_singular_type_label(type):
    if type in labels:
        return labels[type]['singular']
    return type


def get_type_label(type):
    if type in labels:
        return labels[type]['plural']
    return type


def get_long_type_label(type):
    if type in labels:
        return labels[type]['long_plural']
    return type
