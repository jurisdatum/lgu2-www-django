
from typing import Any, Optional
import requests

from django.conf import settings

SERVER = settings.API_BASE_URL

CLML_MIME_TYPE = 'application/xml'
AKN_MIME_TYPE = 'application/akn+xml'


def fix_language(language: Optional[str]) -> Optional[str]:
    if language is None:
        return None
    if language == "welsh" or language == "cy":
        return "cy"
    return "en"


def get(endpoint: str, accept: str, language: Optional[str] = None) -> requests.Response:
    url = SERVER + endpoint
    headers = {'Accept': accept}
    language = fix_language(language)
    if language is not None:
        headers = {'Accept': accept, 'Accept-Language': language}
    return requests.get(url, headers=headers)


def get_json(endpoint: str, language: Optional[str] = None) -> Any:
    return get(endpoint, 'application/json', language).json()


def get_raw_json(endpoint: str, language: Optional[str] = None) -> str:
    return get(endpoint, 'application/json', language).text


def get_clml(endpoint: str, language: Optional[str] = None) -> requests.Response:
    return get(endpoint, CLML_MIME_TYPE, language)


def get_akn(endpoint: str, language: Optional[str] = None) -> requests.Response:
    return get(endpoint, AKN_MIME_TYPE, language)
