
from typing import Optional

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template import loader

from ..api import contents as api
from ..api.document import Meta as DocumentMetadata
from ..messages.status import get_status_message
from ..util.labels import get_type_label


def _should_redirect(type: str, version: str, meta: DocumentMetadata) -> Optional[HttpResponseRedirect]:
    if version is None and meta['status'] == 'final':
        return redirect('document-toc-version', type=meta['shortType'], year=meta['year'], number=meta['number'], version=data['meta']['version'])
    if version is None and meta['shortType'] != type:
        return redirect('document-toc', type=meta['shortType'], year=meta['year'], number=meta['number'])
    if meta['shortType'] != type:
        return redirect('document-toc-version', type=meta['shortType'], year=meta['year'], number=meta['number'], version=meta['version'])


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


def toc(request, type, year, number, version=None):

    data = api.get_toc(type, year, number, version)

    meta = data['meta']

    rdrct = _should_redirect(type, version, meta)
    if rdrct is not None:
        return rdrct

    link_prefix = '/' + data['meta']['id']
    if request.LANGUAGE_CODE == 'cy':
        link_prefix = '/cy' + link_prefix
    link_suffix = '/' + version if version else ''

    _add_all_links(data['contents'], link_prefix, link_suffix)

    data['status_message'] = get_status_message(data['meta'])

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

    template = loader.get_template('document/toc.html')
    return HttpResponse(template.render(data, request))


def data(request, type, year, number, format, version=None):
    if format == 'xml':
        xml = api.get_toc_clml(type, year, number, version)
        return HttpResponse(xml, content_type='application/xml')
    if format == 'akn':
        xml = api.get_toc_akn(type, year, number, version)
        return HttpResponse(xml, content_type='application/xml')
    if format == 'json':
        data = api.get_toc_json(type, year, number, version)
        return HttpResponse(data, content_type='application/json')
