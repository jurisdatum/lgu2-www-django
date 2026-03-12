
from typing import Optional, Union

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.template import loader
from django.utils import timezone

from ..api.document import get_akn, get_clml, get_document, DocumentMetadata
from ..api.pdf import make_pdf_url, make_thumbnail_url
from ..messages.status import build_status
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

    meta['link'] = make_document_link(type, year, number, version, lang)

    timeline = make_timeline_data(meta, "document", lang)
    extent_label = make_combined_extent_label(meta['extent'])
    breadcrumbs = make_breadcrumbs(meta, version, lang)

    status = build_status(meta, timeline)

    is_first_and_only_version = False
    if timeline["original"] and timeline["viewing"]:
        is_first_and_only_version = (
            timeline["viewing"]["label"] == timeline["original"]["label"]
        )

    print("==================================is_first_and_only_version===================")
    print(timeline)
    print(is_first_and_only_version)

    context = {
        "meta": meta,
        "timeline": timeline,
        "extent_label": extent_label,
        "breadcrumbs": breadcrumbs,
        "status": status,
        "article": data["html"],
        "is_first_and_only_version": is_first_and_only_version
    }

    template = loader.get_template("new_theme/document/document.html")
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
