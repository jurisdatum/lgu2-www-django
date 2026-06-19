"""Regression tests: API helpers must not crash when the upstream returns an
error body (typically a 404 'Document Not Found'). Before these guards were
added, the helpers blindly called `convert_dates(doc["meta"])` on the error
body and raised KeyError, surfacing as a 500 to the user."""

from unittest.mock import patch

from django.test import SimpleTestCase

from lgu2.api import contents, document, fragment

ERROR_BODY = {"status": 404, "error": "Document Not Found"}


class GetDocumentNotFoundTests(SimpleTestCase):

    @patch("lgu2.api.document.server.get_json")
    def test_error_body_is_returned_as_is(self, mock_get_json):
        mock_get_json.return_value = ERROR_BODY
        # Cover both branches of the ukia / non-ukia type check.
        for doc_type in ("ukpga", "ukia"):
            with self.subTest(type=doc_type):
                self.assertEqual(document.get_document(doc_type, 9999, 1), ERROR_BODY)


class FragmentGetNotFoundTests(SimpleTestCase):

    @patch("lgu2.api.fragment.server.get_json")
    def test_error_body_is_returned_as_is(self, mock_get_json):
        mock_get_json.return_value = ERROR_BODY
        self.assertEqual(fragment.get("ukpga", 2000, 8, "section-99999"), ERROR_BODY)


class GetTocNotFoundTests(SimpleTestCase):

    @patch("lgu2.api.contents.server.get_json")
    def test_returns_none_for_status_404_with_canonical_message(self, mock_get_json):
        mock_get_json.return_value = ERROR_BODY
        self.assertIsNone(contents.get_toc("ukpga", 9999, 1))

    @patch("lgu2.api.contents.server.get_json")
    def test_returns_none_for_any_error_body_shape(self, mock_get_json):
        # The pre-fix guard only matched the exact canonical shape, so other
        # error bodies fell through to convert_dates and 500'd.
        mock_get_json.return_value = {"error": "anything else"}
        self.assertIsNone(contents.get_toc("ukpga", 9999, 1))
