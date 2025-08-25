from django.conf import settings
import requests

from .search_types import SearchParams
from .browse_types import DocumentList

SERVER = settings.API_BASE_URL


def basic_search(query_params: SearchParams) -> DocumentList:
    """
    Perform a basic search by forwarding query parameters to an external API.

    Args:
        query_params (SearchParams): Well-formed search parameters dictionary.

    Returns:
        DocumentList: Paginated list of legislation documents with metadata.
    """
    api_url = f"{SERVER}/search"

    response = requests.get(api_url, params=query_params)
    response.raise_for_status()
    data = response.json()
    DocumentList.convert_dates(data)
    return data
