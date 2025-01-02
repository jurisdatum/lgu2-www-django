
from datetime import datetime
from typing import Optional, Union

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from ..api import fragment as api
from ..messages.status import get_status_message
from ..util.labels import get_type_label
from ..util.types import get_category
from .document import _make_timeline_data
from .redirect import make_data_redirect, redirect_current, redirect_version
from . import theme
from .helper.data_urls import make_fragment_data_url, make_whole_doc_data_url, make_toc_data_url


# ToDo fix to use response headers
def _should_redirect(type: str, version: Optional[str], lang: Optional[str], meta: api.FragmentMetadata) -> Optional[HttpResponseRedirect]:
    year: Union[int, str] = meta['regnalYear'] if 'regnalYear' in meta else meta['year']
    if version is None and meta['status'] == 'final':
        return redirect_version('fragment', meta['shortType'], year, meta['number'], section=meta['fragment'], version=meta['version'], lang=lang)
    if version is None and meta['shortType'] != type:
        return redirect_current('fragment', meta['shortType'], year, meta['number'], section=meta['fragment'], lang=lang)
    if meta['shortType'] != type:
        return redirect_version('fragment', meta['shortType'], year, meta['number'], section=meta['fragment'], version=meta['version'], lang=lang)


def fragment(request, type: str, year: str, number: str, section: str, version: Optional[str] = None, lang: Optional[str] = None):

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
    except (TypeError, ValueError):
        pit = None

    timeline = _make_timeline_data(data['meta'], pit)

    status_message = get_status_message(data['meta'])

    meta['category'] = get_category(meta['shortType'])

    context = {
        'params': {
            'type': type,
            'year': year,
            'number': number,
            'section': section,
            'version': version,
            'lang': lang
        },
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
    if theme.use_new_theme(request):
        template = loader.get_template('new/default.html')
        context = convert_context_for_new_theme(context)
        response = HttpResponse(template.render(context, request))
        theme.set_new_theme(response)
        return response
    else:
        template = loader.get_template('document/document.html')
        response = HttpResponse(template.render(context, request))
        theme.remove_new_theme(response)
        return response


def convert_context_for_new_theme(context):
    doc_year: int = context['meta']['year']
    doc_num: int = context['meta']['number']
    chapter_label: str = 'Chapter ' + str(doc_num)
    return {
        'breadcrumbs': {
            'heading': 'The Statute Book',
            'levels': [
                ('UK Public General Acts', reverse('browse', args=['ukpga'])),
                (str(doc_year), reverse('browse-year', args=['ukpga', doc_year])),
                (chapter_label + ' (Table of contents)', reverse('toc', args=['ukpga', doc_year, doc_num])),
                ('Part 1', '#'),  # ToDo
                ('Suplimentary', '#'),  # ToDo
                ('Section 25F', '#')  # ToDo
            ]
        },
        'links': {
            'this': {
                'xml': make_fragment_data_url(**context['params'])
            },
            'whole': {
                'xml': make_whole_doc_data_url(**context['params'])
            },
            'toc': {
                'xml': make_toc_data_url(**context['params'])
            }
        }
    }


def _xml_or_redirect(package, section: str, lang: Optional[str], format: str):
    if package['redirect'] is None:
        return HttpResponse(package['xml'], content_type='application/xml')
    else:
        return make_data_redirect('fragment', package['redirect'], lang, format, section=section)


def data(request, type, year, number, section, format, version=None, lang: Optional[str] = None):
    if format == 'xml':
        package = api.get_clml(type, year, number, section, version, lang)
        return _xml_or_redirect(package, section, lang, format)
    if format == 'akn':
        package = api.get_akn(type, year, number, section, version, lang)
        return _xml_or_redirect(package, section, lang, format)
    if format == 'html':
        pass  # ToDo
    if format == 'json':
        pass  # ToDo
    return HttpResponse(status=406)
