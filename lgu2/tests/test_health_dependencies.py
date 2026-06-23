"""Regression: health_dependencies must distinguish three upstream states —
ok (200), unhealthy (non-200 response), and down (transport failure). The
server.get() helper preserves the raw Response so this view can introspect
status_code without going through the get_checked() exception path."""

from unittest.mock import patch

import requests
from django.test import SimpleTestCase

from lgu2.tests._helpers import mock_response


class HealthDependenciesTests(SimpleTestCase):

    @patch("lgu2.api.server.requests.get")
    def test_ok_when_upstream_returns_200(self, mock_get):
        mock_get.return_value = mock_response(200)
        response = self.client.get("/health/dependencies")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["checks"]["api"], "ok")

    @patch("lgu2.api.server.requests.get")
    def test_unhealthy_when_upstream_returns_500(self, mock_get):
        # The raw server.get() must NOT raise on 500 here — otherwise the view
        # cannot tell "responded but unhealthy" apart from "transport failure".
        mock_get.return_value = mock_response(500)
        response = self.client.get("/health/dependencies")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["checks"]["api"], "unhealthy")

    @patch("lgu2.api.server.requests.get")
    def test_down_when_transport_error(self, mock_get):
        mock_get.side_effect = requests.ConnectionError()
        response = self.client.get("/health/dependencies")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["checks"]["api"], "down")

    @patch("lgu2.api.server.requests.get")
    def test_down_when_timeout(self, mock_get):
        # Timeouts raise UpstreamTimeout from the raw helper too (the only
        # exception the raw path raises). The view's except clause catches it.
        mock_get.side_effect = requests.Timeout()
        response = self.client.get("/health/dependencies")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["checks"]["api"], "down")
