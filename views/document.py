
from datetime import datetime

from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect
from django.template import loader

from .. import api
from ..messages.status import get_status_message

def _make_timeline_data(meta, pit):

    min_list_width = 717
    max_item_width = 637
    min_item_width = 142

    versions = meta['versions']
    versions = filter(lambda v: v != 'enacted', versions)
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

    data = api.get_document(type, year, number, version)

    if 'error' in data:
        template = loader.get_template('404.html')
        return HttpResponseNotFound(template.render({}, request))

    if version is None and data['meta']['status'] == 'final':
        return redirect('document-version', type=type, year=year, number=number, version='enacted')

    if version:
        data['meta']['link'] = '/' + data['meta']['id'] + '/' + version
    else:
        data['meta']['link'] = '/' + data['meta']['id']

    try:
        version_date = datetime.strptime(version, '%Y-%m-%d')
        pit = version_date.strftime("%d/%m/%Y")
    except:
        pit = None

    timeline = _make_timeline_data(data['meta'], pit)

    status_message = get_status_message(data['meta'])

    template = loader.get_template('document/document.html')
    context = {
        'meta': data['meta'],
        'pit': pit,
        'timeline': timeline,
        'status_message': status_message,
        'article': data['html']
    }
    return HttpResponse(template.render(context, request))

def document_clml(request, type, year, number, version=None):
    clml = api.get_clml(type, year, number, version)
    return HttpResponse(clml, content_type='application/xml')

def document_akn(request, type, year, number, version=None):
    akn = api.get_akn(type, year, number, version)
    return HttpResponse(akn, content_type='application/xml')
