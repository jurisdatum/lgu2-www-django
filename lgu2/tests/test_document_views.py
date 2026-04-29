from datetime import date
from typing import Optional
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


def _document_response(associated: Optional[list] = None) -> dict:
    return {
        'meta': {
            'id': 'ukpga/2024/1',
            'shortType': 'ukpga',
            'longType': 'UnitedKingdomPublicGeneralAct',
            'year': 2024,
            'number': 1,
            'version': 'enacted',
            'status': 'final',
            'title': 'Test Act 2024',
            'cite': '2024 c. 1',
            'lang': 'en',
            'publisher': "King's Printer of Acts of Parliament",
            'date': date(2024, 1, 1),
            'modified': date(2024, 1, 1),
            'pointInTime': None,
            'extent': ['E', 'W', 'S', 'NI'],
            'formats': ['xml', 'pdf'],
            'altFormats': [],
            'versions': ['enacted'],
            'has': {},
            'schedules': None,
            'associated': associated if associated is not None else [],
            'alternatives': [],
            'altNumbers': [],
            'unappliedEffects': [],
            'upToDate': None,
        },
        'html': '',
    }


def _toc_response_pdf_only(version: str = 'enacted') -> dict:
    return {
        'meta': {
            'id': 'ukpga/2024/1',
            'shortType': 'ukpga',
            'longType': 'UnitedKingdomPublicGeneralAct',
            'year': 2024,
            'number': 1,
            'version': version,
            'status': 'final',
            'title': 'Test Act 2024',
            'cite': '2024 c. 1',
            'lang': 'en',
            'publisher': "King's Printer of Acts of Parliament",
            'date': date(2024, 1, 1),
            'modified': date(2024, 1, 1),
            'pointInTime': None,
            'extent': ['E', 'W', 'S', 'NI'],
            'formats': ['pdf'],
            'altFormats': [{'url': 'http://example.test/a.pdf', 'thumbnail': 'http://example.test/t.png', 'type': 'application/pdf'}],
            'versions': [version],
            'has': {},
            'schedules': None,
            'associated': [],
            'alternatives': [],
            'altNumbers': [],
            'unappliedEffects': [],
            'upToDate': None,
        },
        'contents': None,
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
        self.assertNotContains(response, 'id="legislationStatus"')
        self.assertNotContains(response, 'class="pit-search"')
        self.assertNotContains(response, 'class="legislation-navigation"')
        self.assertNotContains(response, 'Printer Version')
        self.assertNotContains(response, 'received Royal Assent when it was enacted')
        self.assertNotContains(response, 'Legislation text for the whole Act')

    @patch("lgu2.views.document.get_document")
    def test_ukia_document_page_breadcrumbs_link_to_clean_results_pages(self, mock_get_document):
        mock_get_document.return_value = _ukia_response()

        response = self.client.get(reverse('document', args=['ukia', 2024, 1]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'href="{reverse("browse", args=["ukia"])}"')
        self.assertContains(response, f'href="{reverse("browse-year", args=["ukia", 2024])}"')

    @patch("lgu2.views.document.get_document")
    def test_document_page_renders_related_info_when_associated_present(self, mock_get_document):
        mock_get_document.return_value = _document_response(associated=[
            {'type': 'Note', 'title': 'Explanatory Note'},
            {'type': 'Other', 'title': 'Some Other Document'},
        ])

        response = self.client.get(reverse('document-version', args=['ukpga', 2024, 1, 'enacted']))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="explanatory-notes"')
        self.assertContains(response, 'class="associated-documents"')

    @patch("lgu2.views.document.get_document")
    def test_document_page_omits_related_info_sections_when_associated_empty(self, mock_get_document):
        mock_get_document.return_value = _document_response(associated=[])

        response = self.client.get(reverse('document-version', args=['ukpga', 2024, 1, 'enacted']))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'class="explanatory-notes"')
        self.assertNotContains(response, 'class="associated-documents"')


class TocViewTests(SimpleTestCase):

    @patch("lgu2.views.toc.api.get_toc")
    def test_toc_pdf_only_enacted_shows_kings_printer_message(self, mock_get_toc):
        mock_get_toc.return_value = _toc_response_pdf_only(version='enacted')

        response = self.client.get(reverse('toc-version', args=['ukpga', 2024, 1, 'enacted']))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Printer Version')
        self.assertContains(response, 'received Royal Assent when it was enacted')

    @patch("lgu2.views.toc.api.get_toc")
    def test_toc_pdf_only_revised_omits_kings_printer_message(self, mock_get_toc):
        mock_get_toc.return_value = _toc_response_pdf_only(version='2024-06-01')

        response = self.client.get(reverse('toc-version', args=['ukpga', 2024, 1, '2024-06-01']))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Printer Version')
        self.assertNotContains(response, 'received Royal Assent when it was enacted')
        self.assertNotContains(response, 'Legislation text for the whole Act')
