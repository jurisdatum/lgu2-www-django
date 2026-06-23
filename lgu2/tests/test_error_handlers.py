"""Tests for the custom error handlers wired as handler404/handler500.

These cover Django-raised errors (unmatched URL, unhandled view exception),
distinct from the upstream-API failures exercised in test_upstream_middleware."""

from unittest.mock import patch

from django.test import RequestFactory, SimpleTestCase, override_settings
from django.urls import reverse

from lgu2.views.errors import page_not_found, server_error


class ErrorHandlerUnitTests(SimpleTestCase):
    """Call the handlers directly — independent of DEBUG and the resolver."""

    def setUp(self):
        self.factory = RequestFactory()

    def test_page_not_found_renders_new_theme_404(self):
        response = page_not_found(self.factory.get("/nope"), exception=Exception())
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Page Not Found", response.content)

    def test_server_error_renders_branded_page(self):
        response = server_error(self.factory.get("/boom"))
        self.assertEqual(response.status_code, 500)
        self.assertIn(b"Service Temporarily Unavailable", response.content)


@override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
class ErrorHandlerWiringTests(SimpleTestCase):
    """With DEBUG off, Django invokes the configured handlers end-to-end."""

    def test_unmatched_url_uses_new_theme_404(self):
        response = self.client.get("/zzz/not/a/real/page")
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "new_theme/404.html")

    @patch("lgu2.views.document.get_document")
    def test_unhandled_view_exception_uses_new_theme_500(self, mock_get_document):
        # A non-upstream error propagates past UpstreamErrorMiddleware to handler500.
        mock_get_document.side_effect = ValueError("boom")
        self.client.raise_request_exception = False
        response = self.client.get(reverse("document", args=["ukpga", 2024, 1]))
        self.assertEqual(response.status_code, 500)
        self.assertTemplateUsed(response, "new_theme/502.html")


class ErrorHandlerSafeRenderTests(SimpleTestCase):
    """A broken error template must not cascade into a second failure; the
    handler falls back to a static text response with the correct status."""

    @patch("lgu2.views.errors.render")
    def test_broken_template_falls_back_to_static_response(self, mock_render):
        mock_render.side_effect = RuntimeError("broken template")
        response = server_error(RequestFactory().get("/boom"))
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response["Content-Type"], "text/plain")
        self.assertIn(b"Service temporarily unavailable", response.content)
