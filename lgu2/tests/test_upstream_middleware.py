"""End-to-end tests for the UpstreamErrorMiddleware."""

from unittest.mock import patch

from django.test import SimpleTestCase
from django.urls import reverse

from lgu2.api.server import UpstreamError, UpstreamNotFound, UpstreamTimeout


class UpstreamErrorHtmlPagesTests(SimpleTestCase):
    """Browser routes (no `format` resolver kwarg) get the branded HTML page."""

    @patch("lgu2.views.document.get_document")
    def test_exceptions_map_to_status_and_template(self, mock_get_document):
        cases = [
            (UpstreamNotFound(404, "/whatever"), 404, "new_theme/404.html"),
            (UpstreamTimeout("/whatever"), 504, "new_theme/502.html"),
            (UpstreamError(500, "/whatever"), 502, "new_theme/502.html"),
        ]
        for exception, expected_status, expected_template in cases:
            with self.subTest(exception=type(exception).__name__):
                mock_get_document.side_effect = exception
                response = self.client.get(reverse("document", args=["ukpga", 2024, 1]))
                self.assertEqual(response.status_code, expected_status)
                self.assertTemplateUsed(response, expected_template)


class UpstreamErrorDataEndpointTests(SimpleTestCase):
    """Routes whose URL captures `format=json|xml|akn|feed` get a body in the
    matching content-type instead of an HTML error page."""

    @patch("lgu2.views.fragment.api.get")
    def test_json_data_endpoint_returns_json_envelope_on_not_found(self, mock_api_get):
        mock_api_get.side_effect = UpstreamNotFound(404, "/whatever")
        response = self.client.get(
            reverse(
                "fragment-data",
                kwargs={
                    "type": "ukpga",
                    "year": 2024,
                    "number": 1,
                    "section": "section/1",
                    "format": "json",
                },
            )
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(response.json(), {"error": "Not Found", "status": 404})

    @patch("lgu2.views.document.get_clml")
    def test_xml_data_endpoint_returns_xml_content_type_on_not_found(
        self, mock_get_clml
    ):
        mock_get_clml.side_effect = UpstreamNotFound(404, "/whatever")
        response = self.client.get(
            reverse("document-data", args=["ukpga", 2024, 1, "xml"])
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response["Content-Type"], "application/xml")
        self.assertEqual(response.content, b"")

    @patch("lgu2.views.document.get_akn")
    def test_akn_data_endpoint_returns_akn_content_type_on_upstream_error(
        self, mock_get_akn
    ):
        mock_get_akn.side_effect = UpstreamError(500, "/whatever")
        response = self.client.get(
            reverse("document-data", args=["ukpga", 2024, 1, "akn"])
        )
        self.assertEqual(response.status_code, 502)
        self.assertEqual(response["Content-Type"], "application/akn+xml")
        self.assertEqual(response.content, b"")


class UpstreamErrorTransportFailureTests(SimpleTestCase):
    """A transport-level failure (connection refused, DNS, SSL) reaches the
    view as UpstreamError(502) and surfaces as a friendly 502 page rather
    than a Django 500."""

    @patch("lgu2.api.server.requests.get")
    def test_connection_error_renders_502_page(self, mock_requests_get):
        import requests

        mock_requests_get.side_effect = requests.ConnectionError()
        response = self.client.get(reverse("document", args=["ukpga", 2024, 1]))
        self.assertEqual(response.status_code, 502)
        self.assertTemplateUsed(response, "new_theme/502.html")


class UpstreamErrorSafeRenderTests(SimpleTestCase):
    """If the branded error template itself fails to render (broken {% url %},
    missing static, etc.), the middleware must NOT cascade into a Django 500
    — it falls back to a static text response with the correct status."""

    @patch("lgu2.middleware.upstream_errors.render")
    @patch("lgu2.views.document.get_document")
    def test_broken_template_falls_back_to_static_response(
        self, mock_get_document, mock_render
    ):
        mock_get_document.side_effect = UpstreamNotFound(404, "/whatever")
        mock_render.side_effect = RuntimeError("broken template")
        response = self.client.get(reverse("document", args=["ukpga", 2024, 1]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response["Content-Type"], "text/plain")
        self.assertIn(b"Service temporarily unavailable", response.content)
