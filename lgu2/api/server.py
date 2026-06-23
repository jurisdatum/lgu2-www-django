from typing import Any, Optional
import requests

from django.conf import settings

SERVER = settings.API_BASE_URL
DEFAULT_TIMEOUT = settings.API_TIMEOUT

CLML_MIME_TYPE = "application/xml"
AKN_MIME_TYPE = "application/akn+xml"
ATOM_MIME_TYPE = "application/atom+xml"


class UpstreamError(Exception):
    """The upstream API returned a non-2xx response."""

    def __init__(self, status_code: int, endpoint: str):
        self.status_code = status_code
        self.endpoint = endpoint
        super().__init__(f"{status_code} from {endpoint}")


class UpstreamNotFound(UpstreamError):
    """The upstream API returned 404. Subclass so views/middleware can catch
    not-found separately from other upstream failures."""


class UpstreamTimeout(UpstreamError):
    """The request to the upstream API timed out (connect or read)."""

    def __init__(self, endpoint: str):
        super().__init__(504, endpoint)


def fix_language(language: Optional[str]) -> Optional[str]:
    if language is None:
        return None
    if language == "welsh" or language == "cy":
        return "cy"
    return "en"


def _build_headers(accept: Optional[str], language: Optional[str]) -> dict:
    headers = {}
    if accept is not None:
        headers["Accept"] = accept
    language = fix_language(language)
    if language is not None:
        headers["Accept-Language"] = language
    return headers


def get(
    endpoint: str, accept: str, language: Optional[str] = None
) -> requests.Response:
    """Raw GET that returns the Response unchanged. Used by health checks and
    any caller that needs to inspect the status itself. Raises UpstreamTimeout
    on connect/read timeout and UpstreamError(502) on other transport errors
    (connection refused, DNS failure, SSL error). HTTP status checking is the
    caller's job."""
    url = SERVER + endpoint
    headers = _build_headers(accept, language)
    try:
        return requests.get(url, headers=headers, timeout=DEFAULT_TIMEOUT)
    except requests.Timeout:
        raise UpstreamTimeout(endpoint)
    except requests.RequestException:
        raise UpstreamError(502, endpoint)


def head(endpoint: str, language: Optional[str] = None) -> requests.Response:
    url = SERVER + endpoint
    headers = _build_headers(None, language)
    try:
        return requests.head(url, headers=headers, timeout=DEFAULT_TIMEOUT)
    except requests.Timeout:
        raise UpstreamTimeout(endpoint)
    except requests.RequestException:
        raise UpstreamError(502, endpoint)


def get_checked(
    endpoint: str, accept: str, language: Optional[str] = None
) -> requests.Response:
    """GET that raises UpstreamNotFound on 404 and UpstreamError on any other
    non-2xx. The typical entry point for body-parsing helpers below."""
    response = get(endpoint, accept, language)
    if 200 <= response.status_code < 300:
        return response
    cls = UpstreamNotFound if response.status_code == 404 else UpstreamError
    raise cls(response.status_code, endpoint)


def get_json(endpoint: str, language: Optional[str] = None) -> Any:
    return get_checked(endpoint, "application/json", language).json()


def get_raw_json(endpoint: str, language: Optional[str] = None) -> str:
    return get_checked(endpoint, "application/json", language).text


def get_clml(endpoint: str, language: Optional[str] = None) -> requests.Response:
    return get_checked(endpoint, CLML_MIME_TYPE, language)


def get_akn(endpoint: str, language: Optional[str] = None) -> requests.Response:
    return get_checked(endpoint, AKN_MIME_TYPE, language)


def get_atom(endpoint: str, language: Optional[str] = None) -> str:
    return get_checked(endpoint, ATOM_MIME_TYPE, language).text
