
from datetime import datetime
from typing import Optional

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import redirect
from django.template import loader

from ..api import fragment as api
from .document import _make_timeline_data
from ..messages.status import get_status_message
from ..util.labels import get_type_label
from ..util.types import get_category


def _should_redirect(type: str, version: Optional[str], lang: Optional[str], meta: api.FragmentMetadata) -> Optional[HttpResponseRedirect]:
    section = meta['fragment'] if 'fragment' in meta else None
    if version is None and meta['status'] == 'final':
        if lang is None:
            return redirect('fragment-version', type=meta['shortType'], year=meta['year'], number=meta['number'], section=section, version=meta['version'])
        else:
            return redirect('fragment-version-lang', type=meta['shortType'], year=meta['year'], number=meta['number'], section=section, version=meta['version'], lang=lang)
    if version is None and meta['shortType'] != type:
        if lang is None:
            return redirect('fragment', type=meta['shortType'], year=meta['year'], number=meta['number'], section=section)
        else:
            return redirect('fragment-lang', type=meta['shortType'], year=meta['year'], number=meta['number'], section=section, lang=lang)
    if meta['shortType'] != type:
        if lang is None:
            return redirect('fragment-version', type=meta['shortType'], year=meta['year'], number=meta['number'], section=section, version=meta['version'])
        else:
            return redirect('fragment-version-lang', type=meta['shortType'], year=meta['year'], number=meta['number'], section=section, version=meta['version'], lang=lang)


def fragment(request, type, year, number, section, version=None, lang=None):

    data = api.get(type, year, number, section, version, lang)
    # API should add None values to fragment requests
    # but they're current missing for intro and last section
    if 'prev' not in data['meta']:
        data['meta']['prev'] = None
    if 'next' not in data['meta']:
        data['meta']['next'] = None

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
    if data['meta']['prev']:
        data['meta']['prev'] = link_prefix + '/' + data['meta']['prev'] + link_suffix
    if data['meta']['next']:
        data['meta']['next'] = link_prefix + '/' + data['meta']['next'] + link_suffix

    try:
        version_date = datetime.strptime(version, '%Y-%m-%d')
        pit = version_date.strftime("%d/%m/%Y")
    except ValueError:
        pit = None

    timeline = _make_timeline_data(data['meta'], pit)

    status_message = get_status_message(data['meta'])

    meta['category'] = get_category(meta['shortType'])

    context = {
        'meta': data['meta'],
        'pit': pit,
        'type_label_plural': get_type_label(data['meta']['longType']),
        'timeline': timeline,
        'status_message': status_message,
        'article': data['html'],
        'links': {
            'toc': link_prefix + '/contents' + link_suffix,
            'content': link_prefix + '/introduction' + link_suffix,
            'notes': '/',
            'resources': '/',
            'whole': link_prefix + link_suffix,
            'body': None if 'fragment' in data['meta'] and data['meta']['fragment'] == 'body' else link_prefix + '/body' + link_suffix,
            'schedules': None if data['meta']['schedules'] is None else link_prefix + '/schedules' + link_suffix
        }
    }
    template = loader.get_template('document/document.html')
    return HttpResponse(template.render(context, request))


def data(request, type, year, number, section, format, version=None):
    if format == 'xml':
        xml = api.get_clml(type, year, number, section, version)
        return HttpResponse(xml, content_type='application/xml')
    if format == 'akn':
        xml = api.get_akn(type, year, number, section, version)
        return HttpResponse(xml, content_type='application/xml')
