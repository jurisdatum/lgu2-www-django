
from typing import Any
import requests

from django.conf import settings

SERVER = settings.API_BASE_URL

CLML_MIME_TYPE = 'application/xml'
AKN_MIME_TYPE = 'application/akn+xml'


def get(endpoint: str, accept: str) -> requests.Response:
    url = SERVER + endpoint
    headers = {'Accept': accept}
    return requests.get(url, headers=headers)


def get_json(endpoint: str) -> Any:
    return get(endpoint, 'application/json').json()


def get_raw_json(endpoint: str) -> str:
    return get(endpoint, 'application/json').text


def get_clml(endpoint: str) -> requests.Response:
    return get(endpoint, CLML_MIME_TYPE)


def get_akn(endpoint: str) -> requests.Response:
    return get(endpoint, AKN_MIME_TYPE)
