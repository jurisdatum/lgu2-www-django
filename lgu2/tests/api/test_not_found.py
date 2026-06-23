"""Server-layer helpers raise typed exceptions on upstream 404 / 5xx / timeout."""

from unittest.mock import patch

import requests
from django.test import SimpleTestCase

from lgu2.api import contents, document, fragment, server
from lgu2.tests._helpers import mock_response


class ServerGetCheckedTests(SimpleTestCase):

    @patch("lgu2.api.server.requests.get")
    def test_404_raises_upstream_not_found(self, mock_get):
        mock_get.return_value = mock_response(404, body="Not Found")
        with self.assertRaises(server.UpstreamNotFound) as ctx:
            server.get_checked("/whatever", "application/json")
        self.assertEqual(ctx.exception.status_code, 404)
        self.assertEqual(ctx.exception.endpoint, "/whatever")

    @patch("lgu2.api.server.requests.get")
    def test_500_raises_upstream_error(self, mock_get):
        mock_get.return_value = mock_response(500, body="boom")
        with self.assertRaises(server.UpstreamError) as ctx:
            server.get_checked("/whatever", "application/json")
        # assertRaises matches subclasses, so pin the exact type — otherwise a
        # regression that classifies 5xx as UpstreamNotFound would pass.
        self.assertIs(type(ctx.exception), server.UpstreamError)
        self.assertEqual(ctx.exception.status_code, 500)

    @patch("lgu2.api.server.requests.get")
    def test_timeout_raises_upstream_timeout(self, mock_get):
        mock_get.side_effect = requests.Timeout()
        with self.assertRaises(server.UpstreamTimeout) as ctx:
            server.get_checked("/whatever", "application/json")
        self.assertEqual(ctx.exception.status_code, 504)

    @patch("lgu2.api.server.requests.get")
    def test_connection_error_raises_upstream_error_with_502(self, mock_get):
        # Connection refused / DNS failure / SSL error — anything that prevents
        # the request from reaching the upstream at all — should surface as
        # UpstreamError(502) so the middleware renders a Bad Gateway, not a
        # raw Django 500.
        mock_get.side_effect = requests.ConnectionError()
        with self.assertRaises(server.UpstreamError) as ctx:
            server.get_checked("/whatever", "application/json")
        self.assertIs(type(ctx.exception), server.UpstreamError)
        self.assertEqual(ctx.exception.status_code, 502)

    @patch("lgu2.api.server.requests.get")
    def test_200_returns_response(self, mock_get):
        mock_get.return_value = mock_response(200, json_body={"ok": True})
        response = server.get_checked("/whatever", "application/json")
        self.assertEqual(response.status_code, 200)


class ServerGetRawTests(SimpleTestCase):
    """The raw get() preserves the Response on non-2xx for callers that need to
    inspect status themselves (health_check is the load-bearing example)."""

    @patch("lgu2.api.server.requests.get")
    def test_raw_get_returns_response_unchanged_on_500(self, mock_get):
        mock_get.return_value = mock_response(500, body="boom")
        response = server.get("/health", "application/json")
        self.assertEqual(response.status_code, 500)

    @patch("lgu2.api.server.requests.get")
    def test_raw_get_still_raises_on_timeout(self, mock_get):
        mock_get.side_effect = requests.Timeout()
        with self.assertRaises(server.UpstreamTimeout):
            server.get("/health", "application/json")

    @patch("lgu2.api.server.requests.get")
    def test_raw_get_raises_upstream_error_on_connection_error(self, mock_get):
        # health_dependencies catches Exception broadly and maps to "down" —
        # both UpstreamTimeout and UpstreamError are Exception subclasses,
        # so the health view still works either way. But the contract for
        # other callers is that any transport-level failure becomes an
        # UpstreamError subclass.
        mock_get.side_effect = requests.ConnectionError()
        with self.assertRaises(server.UpstreamError):
            server.get("/health", "application/json")


class ApiHelperPropagationTests(SimpleTestCase):
    """Each api/* helper should propagate UpstreamNotFound rather than catching
    it. The previous duck-typed `if "error" in ...` guards are gone."""

    @patch("lgu2.api.document.server.requests.get")
    def test_get_document_propagates_not_found(self, mock_get):
        mock_get.return_value = mock_response(404)
        # Cover both branches of the ukia / non-ukia type check.
        for doc_type in ("ukpga", "ukia"):
            with self.subTest(type=doc_type):
                with self.assertRaises(server.UpstreamNotFound):
                    document.get_document(doc_type, 9999, 1)

    @patch("lgu2.api.fragment.server.requests.get")
    def test_fragment_get_propagates_not_found(self, mock_get):
        mock_get.return_value = mock_response(404)
        with self.assertRaises(server.UpstreamNotFound):
            fragment.get("ukpga", 2000, 8, "section-99999")

    @patch("lgu2.api.contents.server.requests.get")
    def test_get_toc_propagates_not_found(self, mock_get):
        mock_get.return_value = mock_response(404)
        with self.assertRaises(server.UpstreamNotFound):
            contents.get_toc("ukpga", 9999, 1)
