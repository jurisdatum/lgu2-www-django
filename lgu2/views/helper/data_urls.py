
from typing import Optional

from django.urls import reverse


def make_whole_doc_data_url(type: str, year: str, number: str, version: Optional[str], lang: Optional[str], **kwargs) -> str:
    if lang is None:
        if version is None:
            return reverse('document-data', args=[type, year, number, 'xml'])
        else:
            return reverse('document-version-data', args=[type, year, number, version, 'xml'])
    else:
        if version is None:
            return reverse('document-lang-data', args=[type, year, number, lang, 'xml'])
        else:
            return reverse('document-version-lang-data', args=[type, year, number, version, lang, 'xml'])


def make_fragment_data_url(type: str, year: str, number: str, section: str, version: Optional[str], lang: Optional[str]) -> str:
    if lang is None:
        if version is None:
            return reverse('fragment-data', args=[type, year, number, section, 'xml'])
        else:
            return reverse('fragment-version-data', args=[type, year, number, section, version, 'xml'])
    else:
        if version is None:
            return reverse('fragment-lang-data', args=[type, year, number, section, lang, 'xml'])
        else:
            return reverse('fragment-version-lang-data', args=[type, year, number, section, version, lang, 'xml'])


def make_toc_data_url(type: str, year: str, number: str, version: Optional[str], lang: Optional[str], **kwargs) -> str:
    if lang is None:
        if version is None:
            return reverse('toc-data', args=[type, year, number, 'xml'])
        else:
            return reverse('toc-version-data', args=[type, year, number, version, 'xml'])
    else:
        if version is None:
            return reverse('toc-lang-data', args=[type, year, number, lang, 'xml'])
        else:
            return reverse('toc-version-lang-data', args=[type, year, number, version, lang, 'xml'])
