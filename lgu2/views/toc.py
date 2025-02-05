
from typing import Optional, Union

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader

from ..api import contents as api
from ..api.document import DocumentMetadata
from ..api.pdf import make_pdf_url, make_thumbnail_url
from ..messages.status import get_status_message
from ..util.labels import get_type_label
from .redirect import make_data_redirect, redirect_current, redirect_version
from .document import group_effects


# ToDo fix to use response headers
def _should_redirect(type: str, version: Optional[str], lang: Optional[str], meta: DocumentMetadata) -> Optional[HttpResponseRedirect]:
    year: Union[int, str] = meta['regnalYear'] if 'regnalYear' in meta else meta['year']
    if version is None and meta['status'] == 'final':
        return redirect_version('toc', meta['shortType'], year, meta['number'], version=meta['version'], lang=lang)
    if version is None and meta['shortType'] != type:
        return redirect_current('toc', meta['shortType'], year, meta['number'], lang=lang)
    if meta['shortType'] != type:
        return redirect_version('toc', meta['shortType'], year, meta['number'], version=meta['version'], lang=lang)


def _add_all_links(contents, prefix: str, suffix: str):
    if contents is None:
        return

    def add_link(item):
        middle = item['ref'].replace('-', '/')
        item['link'] = prefix + '/' + middle + suffix
        if 'children' in item:
            add_links(item['children'])

    def add_links(items):
        for item in items:
            add_link(item)

    add_links(contents['body'])
    if 'appendices' in contents:
        add_links(contents['appendices'])
    if 'attachmentsBeforeSchedules' in contents:
        add_links(contents['attachmentsBeforeSchedules'])
    if 'schedules' in contents:
        add_links(contents['schedules'])
    if 'attachments' in contents:
        add_links(contents['attachments'])


def toc(request, type: str, year: str, number: str, version: Optional[str] = None, lang: Optional[str] = None):

    data = api.get_toc(type, year, number, version, lang)

    meta = data['meta']

    rdrct = _should_redirect(type, version, lang, meta)
    if rdrct is not None:
        return rdrct

    link_prefix = '/' + data['meta']['id']
    if request.LANGUAGE_CODE == 'cy':
        link_prefix = '/cy' + link_prefix
    link_suffix = ''
    if version:
        link_suffix += '/' + version
    if lang:
        link_suffix += '/' + lang

    _add_all_links(data['contents'], link_prefix, link_suffix)

    data['status'] = {
        'message': get_status_message(data['meta']),
        'label': meta['title'],
        'effects': {
            'direct': group_effects(meta['unappliedEffects'])
        },
        'direct_effects': meta['unappliedEffects'],
        'larger_effects': []
    }

    data['links'] = {
        'toc': link_prefix + '/contents' + link_suffix,
        'content': link_prefix + '/introduction' + link_suffix,
        'notes': '/',
        'resources': '/',
        'whole': link_prefix + link_suffix,
        'body': link_prefix + '/body' + link_suffix,
        'schedules': None if data['meta']['schedules'] is None else link_prefix + '/schedules' + link_suffix
    }

    if data['contents'] is None:
        toc_id = 'viewLegSnippet'
    elif 'schedules' in data['contents']:
        toc_id = 'tocControlsAdded'
    elif any(item.get('name') == 'part' for item in data['contents']['body']):
        toc_id = 'tocControlsAdded'
    else:
        toc_id = 'viewLegSnippet'
    data['toc_id'] = toc_id

    data['type_label_plural'] = get_type_label(data['meta']['longType'])

    if 'pdf' in meta['formats'] and 'xml' not in meta['formats']:
        data['pdf_only'] = True
        data['pdf_link'] = make_pdf_url(type, year, number, version)
        data['pdf_thumb'] = make_thumbnail_url(type, year, number, version)
    else:
        data['pdf_only'] = False
        data['pdf_link'] = None
        data['pdf_thumb'] = None

    template = loader.get_template('document/toc.html')
    return HttpResponse(template.render(data, request))


def _xml_or_redirect(package, lang: Optional[str], format: str):
    if package['redirect'] is None:
        return HttpResponse(package['xml'], content_type='application/xml')
    else:
        return make_data_redirect('toc', package['redirect'], lang, format)


def data(request, type, year, number, format, version=None, lang: Optional[str] = None):
    if format == 'xml':
        package = api.get_toc_clml(type, year, number, version)
        return _xml_or_redirect(package, lang, format)
    if format == 'akn':
        package = api.get_toc_akn(type, year, number, version)
        return _xml_or_redirect(package, lang, format)
    if format == 'html':
        pass  # ToDo
    if format == 'json':
        data = api.get_toc_json(type, year, number, version)
        return HttpResponse(data, content_type='application/json')
    return HttpResponse(status=406)
