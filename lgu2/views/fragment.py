
from datetime import datetime
from typing import Optional, Union

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, JsonResponse
from django.template import loader

from ..api import fragment as api
from ..messages.status import get_status_message_for_fragment
from ..util.labels import get_type_label
from ..util.links import make_contents_link, make_document_link, make_fragment_link
from ..util.types import get_category
from .document import group_effects
from .redirect import make_data_redirect, redirect_current, redirect_version
from .timeline import make_timeline_data_for_fragment
from ..util.extent import make_combined_extent_label
from ..util.breadcrumbs import make_breadcrumbs

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

    data['meta']['link'] = make_document_link(type, year, number, version, lang)
    if data['meta']['prevInfo']:
        data['meta']['prev'] = make_fragment_link(type, year, number, data['meta']['prevInfo']['href'], version, lang)
    if data['meta']['nextInfo']:
        data['meta']['next'] = make_fragment_link(type, year, number, data['meta']['nextInfo']['href'], version, lang)

    try:
        version_date = datetime.strptime(version, '%Y-%m-%d')
        pit = version_date.strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        pit = None

    timeline = make_timeline_data_for_fragment(data['meta'])
    extent_label = make_combined_extent_label(data['meta']['extent'])
    breadcrumbs = make_breadcrumbs(meta, version, lang)
    # associated documents
    explanatory_notes = []
    other_associated_doc = []

    if len(meta['associated']) > 0:
        for associated_documents in meta['associated']:
            if associated_documents['type'] == 'Note':
                explanatory_notes.append(associated_documents)
            else:
                other_associated_doc.append(associated_documents)
    
    

    status_message = get_status_message_for_fragment(data['meta'])

    meta['category'] = get_category(meta['shortType'])

    context = {
        'meta': data['meta'],
        'pit': pit,
        'type_label_plural': get_type_label(data['meta']['longType']),
        'timeline': timeline,
        'extent_label': extent_label,
        'breadcrumbs': breadcrumbs,
        'explanatory_notes': explanatory_notes,
        'other_associated_doc': other_associated_doc,
        'status': {
            'message': status_message,
            'label': meta['fragmentInfo']['label'],
            'effects': {
                'direct': group_effects(meta['unappliedEffects']['fragment']),
                'larger': group_effects(meta['unappliedEffects']['ancestor'])
            },
            'direct_effects': meta['unappliedEffects']['fragment'],
            'larger_effects': meta['unappliedEffects']['ancestor']
        },
        'article': data['html'],
        'links': {
            'toc': make_contents_link(type, year, number, version, lang),
            'content': make_fragment_link(type, year, number, 'introduction', version, lang),
            'notes': '/',
            'resources': '/',
            'whole': make_document_link(type, year, number, version, lang),
            'body': None if 'fragment' in data['meta'] and data['meta']['fragment'] == 'body' else make_fragment_link(type, year, number, 'body', version, lang),
            'schedules': None if data['meta']['schedules'] is None else make_fragment_link(type, year, number, 'schedules', version, lang)
        }
    }
    # template = loader.get_template('document/document.html')
    template = loader.get_template('new_theme/document/document.html')
    return HttpResponse(template.render(context, request))


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
        data = api.get(type, year, number, section, version, lang)
        return JsonResponse(data)
    return HttpResponse(status=406)
