
from datetime import datetime
from typing import Optional, Union

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.template import loader

from ..api.document import get_akn, get_clml, get_document, DocumentMetadata
from ..api.pdf import make_pdf_url, make_thumbnail_url
from ..messages.status import get_status_message
from ..util.labels import get_type_label
from ..util.types import get_category
from .redirect import redirect_current, redirect_version, make_data_redirect


# ToDo fix to use response headers
def _should_redirect(type: str, version: Optional[str], lang: Optional[str], meta: DocumentMetadata) -> Optional[HttpResponseRedirect]:
    year: Union[int, str] = meta['regnalYear'] if 'regnalYear' in meta else meta['year']
    if version is None and meta['status'] == 'final':
        return redirect_version('document', meta['shortType'], year, meta['number'], version=meta['version'], lang=lang)
    if version is None and meta['shortType'] != type:
        return redirect_current('document', meta['shortType'], year, meta['number'], lang=lang)
    if meta['shortType'] != type:
        return redirect_version('document', meta['shortType'], year, meta['number'], version=meta['version'], lang=lang)


def _make_timeline_data(meta, pit):

    min_list_width = 717
    max_item_width = 637
    min_item_width = 142

    versions = meta['versions']
    versions = filter(lambda v: v != 'enacted', versions)
    versions = filter(lambda v: v != 'made', versions)
    versions = filter(lambda v: v != 'prospective', versions)  # ?
    versions = sorted(versions)
    versions = list(map(lambda v: {'date': v}, versions))

    if not versions:
        return None
    elif len(versions) == 1:
        item_width = max_item_width
    elif len(versions) > 4:  # 5?
        item_width = min_item_width
    else:
        item_width = int((min_list_width - 50) / len(versions))
    list_width = len(versions) * item_width + 50
    if list_width < min_list_width:
        list_width = min_list_width

    for version in versions:
        date = datetime.strptime(version['date'], '%Y-%m-%d')
        version['label'] = date.strftime("%d/%m/%Y")
        version['width'] = item_width
        version['current'] = version['date'] == meta['version']
    versions[-1]['width'] = item_width - 40
    return {
        'width': list_width,
        'versions': versions,
        'scroll': list_width > min_list_width
    }


def group_effects(unappliedEffects):
    return {
        'outstanding': [ effect for effect in unappliedEffects if effect['outstanding'] ],
        'future': [ effect for effect in unappliedEffects if effect['required'] and not effect['outstanding'] ],
        'unrequired': [ effect for effect in unappliedEffects if not effect['required'] ]
    }


def document(request, type: str, year: str, number: str, version: Optional[str] = None, lang: Optional[str] = None):

    data = get_document(type, year, number, version, lang)

    if 'error' in data:
        template = loader.get_template('404.html')
        return HttpResponseNotFound(template.render({}, request))

    meta = data['meta']

    rdrct = _should_redirect(type, version, lang, meta)
    if rdrct is not None:
        return rdrct

    link_prefix = '/' + data['meta']['id']
    if request.LANGUAGE_CODE == 'cy':
        link_prefix = '/cy' + link_prefix
    link_suffix = '/' + version if version else ''

    data['meta']['link'] = link_prefix + link_suffix

    try:
        version_date = datetime.strptime(version, '%Y-%m-%d')
        pit = version_date.strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        pit = None

    timeline = _make_timeline_data(data['meta'], pit)

    data['meta']['lang'] = lang
    status = {
        'message': get_status_message(data['meta']),
        'label': meta['title'],
        'effects': {
            'direct': group_effects(meta['unappliedEffects'])
        },
        'direct_effects': meta['unappliedEffects'],
        'larger_effects': []
    }

    meta['category'] = get_category(meta['shortType'])

    if 'pdf' in meta['formats'] and 'xml' not in meta['formats']:
        pdf_only = True
        pdf_link = make_pdf_url(type, year, number, version)
        pdf_thumb = make_thumbnail_url(type, year, number, version)
    else:
        pdf_only = False
        pdf_link = None
        pdf_thumb = None

    context = {
        'meta': data['meta'],
        'pit': pit,
        'type_label_plural': get_type_label(data['meta']['longType']),
        'timeline': timeline,
        'status': status,
        'article': data['html'],
        'links': {
            'toc': link_prefix + '/contents' + link_suffix,
            'content': link_prefix + '/introduction' + link_suffix,
            'notes': '/',
            'resources': '/',
            'whole': None,
            'body': None if 'fragment' in data['meta'] and data['meta']['fragment'] == 'body' else link_prefix + '/body' + link_suffix,
            'schedules': None if data['meta']['schedules'] is None else link_prefix + '/schedules' + link_suffix
        },
        'pdf_only': pdf_only,
        'pdf_link': pdf_link,
        'pdf_thumb': pdf_thumb
    }
    template = loader.get_template('document/document.html')
    return HttpResponse(template.render(context, request))


def _xml_or_redirect(package, lang: Optional[str], format: str):
    if package['redirect'] is None:
        return HttpResponse(package['xml'], content_type='application/xml')
    else:
        return make_data_redirect('document', package['redirect'], lang, format)


def data(request, type: str, year: str, number: int, format: str, version: Optional[str] = None, lang: Optional[str] = None):
    if format == 'xml':
        package = get_clml(type, year, number, version, lang)
        return _xml_or_redirect(package, lang, format)
    if format == 'akn':
        package = get_akn(type, year, number, version, lang)
        return _xml_or_redirect(package, lang, format)
    if format == 'html':
        pass  # ToDo
    if format == 'json':
        pass  # ToDo
    return HttpResponse(status=406)
