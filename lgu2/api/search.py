from django.conf import settings
import requests
from typing import Dict, Any

from .search_types import QueryParams

SERVER = settings.API_BASE_URL


def basic_search(query_params: QueryParams) -> Dict[str, Any]:
    """
    Perform a basic search by forwarding query parameters to an external API.

    Args:
        query_params (QueryParams): Cleaned query parameters dictionary.

    Returns:
        Dict[str, Any]: API response JSON as dictionary.
    """

    # Filter out empty or None values
    cleaned_params = {
        key: value
        for key, value in query_params.items()
        if value is not None and value != ""
    }

    # Final fallback in case of invalid data types (should already be handled earlier)
    if "pageSize" in cleaned_params:
        try:
            cleaned_params["pageSize"] = int(cleaned_params["pageSize"])
        except ValueError:
            cleaned_params["pageSize"] = 20

    api_url = f"{SERVER}/search"

    try:
        response = requests.get(api_url, params=cleaned_params)
        response.raise_for_status()
        api_data = response.json()
    except requests.RequestException as e:
        api_data = {"error": str(e)}

    return api_data
