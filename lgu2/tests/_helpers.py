"""Shared test helpers. Underscore prefix so the Django test discoverer doesn't
treat this file as a test module."""

from unittest.mock import MagicMock


def mock_response(status_code: int, body: str = "", json_body=None) -> MagicMock:
    """Build a MagicMock that quacks like a requests.Response for the attributes
    server.py and its callers inspect: status_code, ok, text, .json(), headers.
    .headers defaults to {} so tests that flow through package_xml (which reads
    response.headers['X-Document-Type']) don't trip a MagicMock subscript error."""
    response = MagicMock()
    response.status_code = status_code
    response.ok = 200 <= status_code < 300
    response.text = body
    response.headers = {}
    response.json.return_value = json_body if json_body is not None else {}
    return response
