
from typing import Optional, Union

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.template import loader
from django.utils import timezone

from ..api.document import get_akn, get_clml, get_document, DocumentMetadata
from ..api.pdf import make_pdf_url, make_thumbnail_url
from ..messages.status import get_status_message
from ..util.labels import get_type_label
from ..util.links import make_contents_link, make_document_link, make_fragment_link
from ..util.types import get_category
from .redirect import make_data_redirect
from ..util.timeline import make_timeline_data
from ..util.extent import make_combined_extent_label
from ..util.breadcrumbs import make_breadcrumbs
from ..util.redirects import should_redirect


def group_effects(unappliedEffects):
    return {
        'outstanding': [effect for effect in unappliedEffects if effect.get('outstanding')],
        'future': [effect for effect in unappliedEffects if effect.get('required') and not effect.get('outstanding')],
        'unrequired': [effect for effect in unappliedEffects if not effect.get('required')]
    }


def document(request, type: str, year: str, number: str, version: Optional[str] = None, lang: Optional[str] = None):

    data = get_document(type, year, number, version, lang)

    if 'error' in data:
        template = loader.get_template('404.html')
        return HttpResponseNotFound(template.render({}, request))

    meta = data['meta']

    rdrct = should_redirect('document', type, version, lang, meta)
    if rdrct is not None:
        return rdrct

    data['meta']['link'] = make_document_link(type, year, number, version, lang)

    timeline = make_timeline_data(data['meta'], "document", lang)
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
        'view_date': meta.get('pointInTime') or timezone.localdate(),
        'type_label_plural': get_type_label(data['meta']['longType']),
        'timeline': timeline,
        'extent_label': extent_label,
        'breadcrumbs': breadcrumbs,
        'explanatory_notes': explanatory_notes,
        'other_associated_doc': other_associated_doc,
        'status': status,
        'article': data['html'],
        'links': {
            'toc': make_contents_link(type, year, number, version, lang),
            'content': make_fragment_link(type, year, number, 'introduction', version, lang),
            'notes': '/',
            'resources': '/',
            'whole': None,
            'body': make_fragment_link(type, year, number, 'body', version, lang),
            'schedules': None if data['meta']['schedules'] is None else make_fragment_link(type, year, number, 'schedules', version, lang)
        },
        'pdf_only': pdf_only,
        'pdf_link': pdf_link,
        'pdf_thumb': pdf_thumb
    }

    template = loader.get_template('new_theme/document/document.html')
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
