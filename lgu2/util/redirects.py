from typing import Optional, Union
from django.http import HttpResponseRedirect
from ..views.redirect import redirect_current, redirect_version

def should_redirect(
    target: str,                # 'document', 'toc', or 'fragment'
    type: str,
    version: Optional[str],
    lang: Optional[str],
    meta,
) -> Optional[HttpResponseRedirect]:
    """
    Generic redirect helper used by document/toc/fragment views.
    """
    year: Union[int, str] = meta['regnalYear'] if 'regnalYear' in meta else meta['year']

    # extra kwargs (for fragment redirects)
    extra_kwargs = {}
    if target == 'fragment' and 'fragment' in meta:
        extra_kwargs['section'] = meta['fragment']

    if version is None and meta['status'] == 'final':
        return redirect_version(target, meta['shortType'], year, meta['number'],
                                version=meta['version'], lang=lang, **extra_kwargs)

    if version is None and meta['shortType'] != type:
        return redirect_current(target, meta['shortType'], year, meta['number'],
                                lang=lang, **extra_kwargs)

    if meta['shortType'] != type:
        return redirect_version(target, meta['shortType'], year, meta['number'],
                                version=meta['version'], lang=lang, **extra_kwargs)

    return None
