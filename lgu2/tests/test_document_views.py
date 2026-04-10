from unittest.mock import patch

from django.http import HttpResponseRedirect
from django.test import SimpleTestCase
from django.urls import reverse


def _ukia_response(pdf_url: str = 'https://example.test/ukia.pdf') -> dict:
    return {
        'meta': {
            'shortType': 'ukia',
            'longType': 'UnitedKingdomImpactAssessment',
            'year': 2024,
            'number': 1,
            'title': 'Test Impact Assessment',
            'altFormats': [{
                'url': pdf_url,
                'thumbnail': 'https://example.test/ukia.png',
                'type': 'application/pdf',
            }],
        },
    }


class DocumentViewTests(SimpleTestCase):

    @patch("lgu2.views.document.should_redirect")
    @patch("lgu2.views.document.get_document")
    def test_document_view_returns_redirect_response(self, mock_get_document, mock_should_redirect):
        expected_location = reverse('document-version', args=['ukpga', 2024, 1, '2024-01-01'])

        mock_get_document.return_value = {
            'meta': {},
            'html': '',
        }
        mock_should_redirect.return_value = HttpResponseRedirect(expected_location)

        response = self.client.get(reverse('document', args=['ukpga', 2024, 1]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], expected_location)

    @patch("lgu2.views.document.get_document")
    def test_ukia_document_page_renders_pdf_and_title(self, mock_get_document):
        pdf_url = 'https://example.test/ukia-2024-1.pdf'
        mock_get_document.return_value = _ukia_response(pdf_url)

        response = self.client.get(reverse('document', args=['ukia', 2024, 1]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, pdf_url)
        self.assertContains(response, 'Test Impact Assessment')
        self.assertNotContains(response, 'src=""')

    @patch("lgu2.views.document.get_document")
    def test_ukia_page_omits_legislation_only_sections(self, mock_get_document):
        mock_get_document.return_value = _ukia_response()

        response = self.client.get(reverse('document', args=['ukia', 2024, 1]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateNotUsed(response, 'new_theme/document/timeline.html')
        self.assertTemplateNotUsed(response, 'new_theme/document/right_side_panel.html')
        self.assertNotContains(response, 'class="pit-search"')
        self.assertNotContains(response, 'class="legislation-navigation"')
