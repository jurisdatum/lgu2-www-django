from django.conf import settings
import requests
from typing import Dict, Any

from .search_types import SearchParams

SERVER = settings.API_BASE_URL


def basic_search(query_params: SearchParams) -> Dict[str, Any]:
    """
    Perform a basic search by forwarding query parameters to an external API.

    Args:
        query_params (SearchParams): Well-formed search parameters dictionary.

    Returns:
        Dict[str, Any]: API response JSON as dictionary.
    """
    api_url = f"{SERVER}/search"

    try:
        response = requests.get(api_url, params=query_params)
        response.raise_for_status()
        api_data = response.json()
    except requests.RequestException as e:
        api_data = {"error": str(e)}

    return api_data
