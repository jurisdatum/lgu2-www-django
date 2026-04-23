from django.test import SimpleTestCase

from lgu2.api.pdf import get_pdf_alt_format, get_pdf_link_and_thumb


def _alt(type: str, **overrides) -> dict:
    # Keep this fixture minimal: the PDF helpers only read type, url, and thumbnail.
    return {'type': type, 'url': 'http://example.test/x', 'thumbnail': 'http://example.test/t', **overrides}


class GetPdfAltFormatTests(SimpleTestCase):

    def test_empty_list_returns_none(self):
        self.assertIsNone(get_pdf_alt_format([]))

    def test_single_pdf_returned(self):
        pdf = _alt('application/pdf')
        self.assertEqual(get_pdf_alt_format([pdf]), pdf)

    def test_no_pdf_returns_none(self):
        self.assertIsNone(get_pdf_alt_format([_alt('image/jpeg'), _alt('text/xml')]))

    def test_pdf_found_when_not_first(self):
        jpeg = _alt('image/jpeg')
        pdf = _alt('application/pdf')
        self.assertEqual(get_pdf_alt_format([jpeg, pdf]), pdf)

    def test_first_pdf_returned_when_multiple(self):
        en = _alt('application/pdf', url='http://example.test/en.pdf')
        cy = _alt('application/pdf', url='http://example.test/cy.pdf')
        self.assertEqual(get_pdf_alt_format([en, cy]), en)


class GetPdfLinkAndThumbTests(SimpleTestCase):

    def test_empty_list_returns_none_pair(self):
        self.assertEqual(get_pdf_link_and_thumb([]), (None, None))

    def test_no_pdf_returns_none_pair(self):
        self.assertEqual(get_pdf_link_and_thumb([_alt('image/jpeg')]), (None, None))

    def test_pdf_returns_url_and_thumbnail(self):
        pdf = _alt('application/pdf', url='http://example.test/a.pdf', thumbnail='http://example.test/a.png')
        self.assertEqual(get_pdf_link_and_thumb([pdf]), ('http://example.test/a.pdf', 'http://example.test/a.png'))
