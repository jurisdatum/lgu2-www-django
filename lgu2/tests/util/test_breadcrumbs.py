from django.test import SimpleTestCase
from django.urls import reverse

from lgu2.util.breadcrumbs import make_breadcrumbs


def _meta(short_type: str = 'ukpga', year: int = 2023, number: int = 1) -> dict:
    return {'shortType': short_type, 'year': year, 'number': number}


class MakeBreadcrumbsTests(SimpleTestCase):

    def test_primary_doc_default_has_chapter_label_and_toc_link(self):
        crumbs = make_breadcrumbs(_meta('ukpga'), version=None, lang=None)
        self.assertEqual(len(crumbs), 3)
        self.assertEqual(crumbs[2]['text'], 'Chapter 1 (Table of Contents)')
        self.assertEqual(crumbs[2]['link'], reverse('toc', args=['ukpga', 2023, 1]))

    def test_secondary_doc_default_has_number_label_and_toc_link(self):
        crumbs = make_breadcrumbs(_meta('uksi'), version=None, lang=None)
        self.assertEqual(crumbs[2]['text'], 'Number 1 (Table of Contents)')
        self.assertEqual(crumbs[2]['link'], reverse('toc', args=['uksi', 2023, 1]))

    def test_with_version_uses_versioned_toc_link(self):
        crumbs = make_breadcrumbs(_meta('ukpga'), version='2024-01-01', lang=None)
        self.assertEqual(crumbs[2]['link'], reverse('toc-version', args=['ukpga', 2023, 1, '2024-01-01']))

    def test_with_lang_uses_lang_toc_link(self):
        crumbs = make_breadcrumbs(_meta('ukpga'), version=None, lang='welsh')
        self.assertEqual(crumbs[2]['link'], reverse('toc-lang', args=['ukpga', 2023, 1, 'welsh']))

    def test_no_toc_omits_table_of_contents_label(self):
        crumbs = make_breadcrumbs(_meta('ukia'), version=None, lang=None, has_toc=False)
        self.assertEqual(crumbs[2]['text'], 'Number 1')
        self.assertNotIn('Table of Contents', crumbs[2]['text'])

    def test_no_toc_links_to_document_page(self):
        crumbs = make_breadcrumbs(_meta('ukia'), version=None, lang=None, has_toc=False)
        self.assertEqual(crumbs[2]['link'], reverse('document', args=['ukia', 2023, 1]))

    def test_first_two_crumbs_unchanged_by_has_toc(self):
        with_toc = make_breadcrumbs(_meta('ukpga'), version=None, lang=None, has_toc=True)
        without_toc = make_breadcrumbs(_meta('ukpga'), version=None, lang=None, has_toc=False)
        self.assertEqual(with_toc[0], without_toc[0])
        self.assertEqual(with_toc[1], without_toc[1])
