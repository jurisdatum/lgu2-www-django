from typing import Optional
from django.http import HttpResponse, HttpResponseNotFound
from django.template import loader
from django.utils import timezone


from ..messages.status import build_status
from ..api.associated import AssociatedDocument
from ..api.document import get_akn, get_clml, get_document
from ..api.pdf import get_pdf_link_and_thumb
from ..messages.status import get_status_message
from ..util.labels import get_type_label
from ..util.links import make_contents_link, make_document_link, make_fragment_link
from ..util.types import get_category
from .redirect import make_data_redirect
from ..util.timeline import make_timeline_data
from ..util.extent import make_combined_extent_label
from ..util.breadcrumbs import make_breadcrumbs, LEGISLATION_BREADCRUMB_HEADING
from ..util.redirects import should_redirect
from .helper.status import make_pdf_status_message


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

    if type == 'ukia':
        context = make_ukia_data(data, version, lang)
    else:
        context = make_document_context(data, type, year, number, version, lang)

    if isinstance(context, HttpResponse):
        return context

    template = loader.get_template('new_theme/document/document.html')
    return HttpResponse(template.render(context, request))


def make_document_context(data, type, year, number, version, lang):

    meta = data['meta']

    rdrct = should_redirect('document', type, version, lang, meta)
    if rdrct is not None:
        return rdrct

    meta['link'] = make_document_link(type, year, number, version, lang)

    timeline = make_timeline_data(meta, "document", lang)
    extent_label = make_combined_extent_label(meta['extent'])
    breadcrumbs = make_breadcrumbs(meta, version, lang)

    explanatory_notes = []
    other_associated_doc = []

    status = build_status(meta, timeline)

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
        pdf_link, pdf_thumb = get_pdf_link_and_thumb(meta['altFormats'])
    else:
        pdf_only = False
        pdf_link = None
        pdf_thumb = None

    context = {
        'meta': meta,
        'view_date': meta.get('pointInTime') or timezone.localdate(),
        'type_label_plural': get_type_label(meta['longType']),
        'timeline': timeline,
        'extent_label': extent_label,
        'breadcrumbs': breadcrumbs,
        'breadcrumb_heading': LEGISLATION_BREADCRUMB_HEADING,
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
            'schedules': None if meta['schedules'] is None else make_fragment_link(type, year, number, 'schedules', version, lang)
        },
        'pdf_only': pdf_only,
        'pdf_link': pdf_link,
        'pdf_thumb': pdf_thumb,
        'status_message': make_pdf_status_message(meta),
    }

    return context


def make_ukia_data(data: AssociatedDocument, version, lang):
    meta = data['meta']
    breadcrumbs = make_breadcrumbs(meta, version, lang, has_toc=False)
    pdf_link, pdf_thumb = get_pdf_link_and_thumb(meta['altFormats'])
    return {
        'meta': meta,
        'breadcrumbs': breadcrumbs,
        # UKIAs are currently always PDF-only. When the API gains html/xml
        # for impact assessments, derive this from the response shape.
        'pdf_only': True,
        'pdf_link': pdf_link,
        'pdf_thumb': pdf_thumb,
    }


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
