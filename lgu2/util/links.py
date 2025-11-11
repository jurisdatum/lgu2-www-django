
from typing import Optional

from django.urls import reverse

from lgu2.api.browse_types import DocEntry
from lgu2.util.types import to_short_type


first_versions = { 'enacted', 'made', 'created', 'adopted' }


def make_contents_link_for_list_entry(doc: DocEntry):
    if doc['id'].endswith('.pdf'):  # correction slips
        return reverse('toc', args=[ to_short_type(doc['longType']), doc['year'], doc['number'] ])
    elif doc['version'] in first_versions:
        return reverse('toc-version', args=[ to_short_type(doc['longType']), doc['year'], doc['number'], doc['version'] ])
    else:
        return reverse('toc', args=[ to_short_type(doc['longType']), doc['year'], doc['number'] ])


def make_contents_link(type: str, year: str, number: str, version: Optional[str], lang: Optional[str]):
    """Return the canonical table-of-contents URL.

    ``lang`` must be one of the language slugs accepted by the views (``english``/``welsh``).
    Pass the view argument through unchanged; API metadata exposes ISO codes (``en``/``cy``)
    that should not be routed here.
    """
    if lang:
        if version:
            return reverse('toc-version-lang', args=[ type, year, number, version, lang ])
        else:
            return reverse('toc-lang', args=[ type, year, number, lang ])
    else:
        if version:
            return reverse('toc-version', args=[ type, year, number, version ])
        else:
            return reverse('toc', args=[ type, year, number ])


def make_fragment_link(type: str, year: str, number: str, fragment: str, version: Optional[str], lang: Optional[str]):
    """Return the fragment URL for a document or schedule entry.

    ``lang`` must be the language slug from the fragment view arguments (``english``/``welsh``),
    not an API ``en``/``cy`` code.
    """
    if lang:
        if version:
            return reverse('fragment-version-lang', args=[ type, year, number, fragment, version, lang ])
        else:
            return reverse('fragment-lang', args=[ type, year, number, fragment, lang ])
    else:
        if version:
            return reverse('fragment-version', args=[ type, year, number, fragment, version ])
        else:
            return reverse('fragment', args=[ type, year, number, fragment ])


def make_document_link(type: str, year: str, number: str, version: Optional[str], lang: Optional[str]):
    """Return the base document URL.

    ``lang`` must match the document view's URL parameters (``english``/``welsh``). Avoid passing
    the API metadata language codes, which are ``en``/``cy``.
    """
    if lang:
        if version:
            return reverse('document-version-lang', args=[ type, year, number, version, lang ])
        else:
            return reverse('document-lang', args=[ type, year, number, lang ])
    else:
        if version:
            return reverse('document-version', args=[ type, year, number, version ])
        else:
            return reverse('document', args=[ type, year, number ])


def make_document_resources_link(type: str, year: str, number: str):
    return reverse('more-resources', args=[ type, year, number ])
