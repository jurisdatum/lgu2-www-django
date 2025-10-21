from django.test import TestCase

from lgu2.views.search import build_browse_url_if_possible, make_smart_link


class TestSmartUrlGeneration(TestCase):
    def test_build_browse_url_simple_type(self):
        params = {'type': 'ukpga'}
        result = build_browse_url_if_possible(params)
        self.assertEqual(result, '/ukpga')

    def test_build_browse_url_type_and_year(self):
        params = {'type': 'ukpga', 'year': 2024}
        result = build_browse_url_if_possible(params)
        self.assertEqual(result, '/ukpga/2024')

    def test_build_browse_url_with_pagination(self):
        params = {'type': 'ukpga', 'year': 2024, 'page': 2}
        result = build_browse_url_if_possible(params)
        self.assertEqual(result, '/ukpga/2024?page=2')

    def test_build_browse_url_complex_search_returns_none(self):
        params = {'type': 'ukpga', 'title': 'housing'}
        result = build_browse_url_if_possible(params)
        self.assertIsNone(result)

    def test_build_browse_url_invalid_type_returns_none(self):
        params = {'type': 'invalid'}
        result = build_browse_url_if_possible(params)
        self.assertIsNone(result)

    def test_make_smart_link_uses_browse_url(self):
        params = {'type': 'ukpga', 'year': 2024}
        result = make_smart_link(params)
        self.assertEqual(result, '/ukpga/2024')

    def test_make_smart_link_fallback_to_search(self):
        params = {'type': 'ukpga', 'title': 'housing'}
        result = make_smart_link(params)
        self.assertTrue(result.startswith('/search/?'))
        self.assertIn('type=ukpga', result)
        self.assertIn('title=housing', result)

    def test_type_and_subject_initial(self):
        params = {'type': 'uksi', 'subject': 'a'}
        result = make_smart_link(params)
        self.assertEqual(result, '/uksi/a')
