from django.conf import settings
import requests

SERVER = settings.API_BASE_URL


def basic_search(query_params):
    """
    Perform a basic search by forwarding query parameters to an external API.

    Args:
        query_params (HttpRequest.GET): Query parameters from the Django request object.

    Returns:
        tuple: (API response JSON as dict, original query parameters as dict)
    """
    # Extract query parameters from the request
    raw_params = query_params.GET.dict()

    # Filter out empty values
    cleaned_params = {key: value for key, value in raw_params.items() if value}

    # Attempt to convert 'pageSize' to int, fallback to default if conversion fails
    if 'pageSize' in cleaned_params:
        try:
            cleaned_params['pageSize'] = int(cleaned_params['pageSize'])
        except ValueError:
            cleaned_params['pageSize'] = 20  # Default fallback value

    api_url = f"{SERVER}/search"

    try:
        response = requests.get(api_url, params=cleaned_params)
        response.raise_for_status()
        api_data = response.json()
    except requests.RequestException as e:
        api_data = {"error": str(e)}

    return api_data, dict(raw_params)


