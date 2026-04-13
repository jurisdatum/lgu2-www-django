from unittest.mock import patch

from django.test import RequestFactory, TestCase
from django.urls import reverse

from lgu2.views.search import build_browse_url_if_possible, extract_query_params, make_smart_link


def _search_response(documents=None, counts=None, query=None):
    documents = documents or []
    counts = counts or {}
    return {
        'meta': {
            'page': 1,
            'totalPages': 1,
            'query': query or {},
            'subjects': [],
            'counts': {
                'total': len(documents),
                'byType': counts.get('byType', []),
                'byYear': counts.get('byYear', []),
                'bySubjectInitial': counts.get('bySubjectInitial', []),
                'byStage': counts.get('byStage', []),
                'byDepartment': counts.get('byDepartment', []),
            },
        },
        'documents': documents,
    }


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

    def test_ukia_search_redirects_to_clean_results_url(self):
        response = self.client.get(reverse('search'), {'type': 'ukia'})
        self.assertRedirects(response, reverse('browse', args=['ukia']), fetch_redirect_response=False)

    @patch('lgu2.views.search.basic_search')
    def test_ukia_clean_results_page_uses_document_links(self, mock_basic_search):
        mock_basic_search.return_value = _search_response(
            documents=[{
                'id': 'ukia/2024/1',
                'year': 2024,
                'number': 1,
                'title': 'Example impact assessment',
                'cite': 'UKIA 2024/1',
                'longType': 'UnitedKingdomImpactAssessment',
                'version': 'enacted',
            }],
            counts={
                'byType': [{
                    'type': 'UnitedKingdomImpactAssessment',
                    'count': 1,
                }],
            },
            query={'type': 'ukia'},
        )

        response = self.client.get(reverse('browse', args=['ukia']))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'href="{reverse("document", args=["ukia", 2024, 1])}"')
        self.assertNotContains(response, reverse('toc', args=['ukia', 2024, 1]))

    @patch('lgu2.views.search.basic_search')
    def test_ukia_year_results_page_uses_document_links(self, mock_basic_search):
        mock_basic_search.return_value = _search_response(
            documents=[{
                'id': 'ukia/2024/1',
                'year': 2024,
                'number': 1,
                'title': 'Example impact assessment',
                'cite': 'UKIA 2024/1',
                'longType': 'UnitedKingdomImpactAssessment',
                'version': 'enacted',
            }],
            counts={
                'byType': [{
                    'type': 'UnitedKingdomImpactAssessment',
                    'count': 1,
                }],
                'byYear': [{
                    'year': 2024,
                    'count': 1,
                }],
            },
            query={'type': 'ukia', 'year': 2024},
        )

        response = self.client.get(reverse('browse-year', args=['ukia', 2024]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'href="{reverse("document", args=["ukia", 2024, 1])}"')
        self.assertNotContains(response, reverse('toc', args=['ukia', 2024, 1]))


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
