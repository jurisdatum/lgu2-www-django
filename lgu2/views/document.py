
from datetime import datetime

from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect
from django.template import loader

from ..api.document import get_akn, get_clml, get_document
from ..messages.status import get_status_message
from ..util.labels import get_type_label_plural
from ..util.types import get_category

def _make_timeline_data(meta, pit):

    min_list_width = 717
    max_item_width = 637
    min_item_width = 142

    versions = meta['versions']
    versions = filter(lambda v: v != 'enacted', versions)
    versions = filter(lambda v: v != 'made', versions)
    versions = filter(lambda v: v != 'prospective', versions) # ?
    versions = sorted(versions)
    versions = list(map(lambda v: { 'date': v }, versions))

    if not versions:
        return None
    elif len(versions) == 1:
        item_width = max_item_width
    elif len(versions) > 4: # 5?
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

def document(request, type, year, number, version=None):

    data = get_document(type, year, number, version)

    if 'error' in data:
        template = loader.get_template('404.html')
        return HttpResponseNotFound(template.render({}, request))

    meta = data['meta']

    if version is None and meta['status'] == 'final':
        return redirect('document-version', type=meta['shortType'], year=meta['year'], number=meta['number'], version=meta['version'])
    if version is None and meta['shortType'] != type:
        return redirect('document', type=meta['shortType'], year=meta['year'], number=meta['number'])
    if meta['shortType'] != type:
        return redirect('document-version', type=meta['shortType'], year=meta['year'], number=meta['number'], version=meta['version'])

    link_prefix = '/' + data['meta']['id']
    if request.LANGUAGE_CODE == 'cy':
        link_prefix = '/cy' + link_prefix
    link_suffix = '/' + version if version else ''

    data['meta']['link'] = link_prefix + link_suffix

    try:
        version_date = datetime.strptime(version, '%Y-%m-%d')
        pit = version_date.strftime("%d/%m/%Y")
    except:
        pit = None

    timeline = _make_timeline_data(data['meta'], pit)

    status_message = get_status_message(data['meta'])

    meta['category'] = get_category(meta['shortType'])

    context = {
        'meta': data['meta'],
        'pit': pit,
        'type_label_plural': get_type_label_plural(data['meta']['longType']),
        'timeline': timeline,
        'status_message': status_message,
        'article': data['html'],
        'links': {
            'toc': link_prefix + '/contents' + link_suffix,
            'content': link_prefix + '/introduction' + link_suffix,
            'notes': '/',
            'resources': '/',
            'whole': None,
            'body': None if 'fragment' in data['meta'] and data['meta']['fragment'] == 'body' else link_prefix + '/body' + link_suffix,
            'schedules': None if data['meta']['schedules'] is None else link_prefix + '/schedules' + link_suffix

        }
    }
    template = loader.get_template('document/document.html')
    return HttpResponse(template.render(context, request))

def document_clml(request, type, year, number, version=None):
    clml = get_clml(type, year, number, version)
    return HttpResponse(clml, content_type='application/xml')

def document_akn(request, type, year, number, version=None):
    akn = get_akn(type, year, number, version)
    return HttpResponse(akn, content_type='application/xml')
