
from typing import List, Optional, Tuple, Union

from .associated import AltFormat
from .server import SERVER


Number = Union[str, int]

PDF_MIME_TYPE = 'application/pdf'


def make_pdf_url(type: str, year: Number, number: Number, version: Optional[str] = None) -> str:
    url = SERVER + '/pdf/' + type + '/' + str(year) + '/' + str(number)
    if version:
        url += '?version=' + version
    return url


def make_thumbnail_url(type: str, year: Number, number: Number, version: Optional[str] = None) -> str:
    url = SERVER + '/thumbnail/' + type + '/' + str(year) + '/' + str(number)
    if version:
        url += '?version=' + version
    return url


def get_pdf_alt_format(alt_formats: List[AltFormat]) -> Optional[AltFormat]:
    """Return the first alt format with MIME type 'application/pdf', or None."""
    return next((fmt for fmt in alt_formats if fmt['type'] == PDF_MIME_TYPE), None)


def get_pdf_link_and_thumb(alt_formats: List[AltFormat]) -> Tuple[Optional[str], Optional[str]]:
    """Return (url, thumbnail) of the first PDF alt format, or (None, None)."""
    pdf = get_pdf_alt_format(alt_formats)
    if pdf is None:
        return None, None
    return pdf['url'], pdf['thumbnail']
