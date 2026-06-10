from typing import Any, Dict

from django.conf import settings
import requests

from .search_types import ApiSearchRequest
from .browse_types import DocumentList

SERVER = settings.API_BASE_URL


def basic_search(query_params: ApiSearchRequest) -> DocumentList:
    """Forward a search request to the external API."""
    api_url = f"{SERVER}/search"
    response = requests.get(api_url, params=_to_wire(query_params))
    response.raise_for_status()
    data = response.json()
    DocumentList.convert_dates(data)
    return data


def _to_wire(params: ApiSearchRequest) -> Dict[str, Any]:
    """Coerce Python values to HTTP-query-string-friendly forms.

    `requests` serialises booleans as Python repr ("True"/"False"); the
    API expects lowercase "true"/"false".
    """
    out: Dict[str, Any] = {}
    for key, value in params.items():
        out[key] = _coerce(value)
    return out


def _coerce(value: Any) -> Any:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return [_coerce(v) for v in value]
    return value
