from django.test import RequestFactory, TestCase

from lgu2.views.search import build_browse_url_if_possible, extract_query_params, make_smart_link


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


class ExtractQueryParamsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_type_all_is_dropped(self):
        # The form sends type=all to mean "no type filter"; the API expects
        # the parameter to be omitted entirely in that case.
        request = self.factory.get('/search/?type=all')
        params = extract_query_params(request)
        self.assertNotIn('type', params)

    def test_type_all_alongside_specific_type_keeps_specific_only(self):
        request = self.factory.get('/search/?type=all&type=ukpga')
        params = extract_query_params(request)
        self.assertEqual(params.get('type'), 'ukpga')

    def test_specific_type_passes_through(self):
        request = self.factory.get('/search/?type=ukpga')
        params = extract_query_params(request)
        self.assertEqual(params.get('type'), 'ukpga')
