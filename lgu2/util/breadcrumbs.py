
from typing import Optional
from django.urls import reverse
from ..api.document import DocumentMetadata
from ..util.labels import get_type_label
from ..util.types import get_category


def make_breadcrumbs(meta: DocumentMetadata, version: Optional[str], lang: Optional[str]):
    doc_type = meta['shortType']
    year = meta['year']
    number = str(meta['number'])
    doc_label = 'Chapter' if get_category(doc_type) == 'primary' else 'Number'
    doc_label += ' ' + number + ' (Table of Contents)'
    if version is None:
        if lang is None:
            toc_link = reverse('toc', args=[doc_type, year, number])
        else:
            toc_link = reverse('toc-lang', args=[doc_type, year, number, lang])
    else:
        if lang is None:
            toc_link = reverse('toc-version', args=[doc_type, year, number, version])
        else:
            toc_link = reverse('toc-version-lang', args=[doc_type, year, number, version, lang])
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
            'link': toc_link  # I wish this could be None
        }
    ]