
from typing import Optional
from django.urls import reverse
from ..api.document import DocumentMetadata
from ..util.labels import get_type_label
from ..util.links import make_contents_link, make_document_link
from ..util.types import get_category

LEGISLATION_BREADCRUMB_HEADING = 'Where this legislation sits in the Statute Book'


def make_breadcrumbs(meta: DocumentMetadata, version: Optional[str], lang: Optional[str], has_toc: bool = True):
    doc_type = meta['shortType']
    year = meta['year']
    number = str(meta['number'])
    doc_label = 'Chapter' if get_category(doc_type) == 'primary' else 'Number'
    doc_label += ' ' + number
    if has_toc:
        doc_label += ' (Table of Contents)'
        last_link = make_contents_link(doc_type, year, number, version, lang)
    else:
        last_link = make_document_link(doc_type, year, number, version, lang)
    return [
        {
            'text': get_type_label(doc_type),
            'link': reverse('browse', args=[doc_type])
        },
        {
            'text': str(year),
            'link': reverse('browse-year', args=[doc_type, year])
        },
        {
            'text': doc_label,
            'link': last_link
        }
    ]
