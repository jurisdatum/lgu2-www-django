
from typing import Optional, Union

from django.http import HttpResponseRedirect
from django.shortcuts import redirect


def redirect_current(url_name: str, type: str, year: Union[int, str], number: Union[int, str], lang: Optional[str], section: Optional[str] = None) -> HttpResponseRedirect:
    if section is None:
        if lang is None:
            return redirect(url_name, type=type, year=year, number=number)
        else:
            return redirect(url_name + '-lang', type=type, year=year, number=number, lang=lang)
    else:
        if lang is None:
            return redirect(url_name, type=type, year=year, number=number, section=section)
        else:
            return redirect(url_name + '-lang', type=type, year=year, number=number, section=section, lang=lang)


def redirect_version(url_name: str, type: str, year: Union[int, str], number: Union[int, str], version: str, lang: Optional[str], section: Optional[str] = None) -> HttpResponseRedirect:
    if section is None:
        if lang is None:
            return redirect(url_name + '-version', type=type, year=year, number=number, version=version)
        else:
            return redirect(url_name + '-version-lang', type=type, year=year, number=number, version=version, lang=lang)
    else:
        if lang is None:
            return redirect(url_name + '-version', type=type, year=year, number=number, section=section, version=version)
        else:
            return redirect(url_name + '-version-lang', type=type, year=year, number=number, section=section, version=version, lang=lang)
