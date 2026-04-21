from unittest.mock import patch

from django.test import RequestFactory, TestCase
from django.urls import resolve

from lgu2.views.search import (
    browse,
    build_browse_url_if_possible,
    extract_query_params,
    make_smart_link,
    replace_param_and_make_smart_link,
)


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

    def test_build_browse_url_with_title_filter_keeps_title_in_query_string(self):
        params = {'type': 'ukpga', 'title': 'housing'}
        result = build_browse_url_if_possible(params)
        self.assertEqual(result, '/ukpga?title=housing')

    def test_build_browse_url_invalid_type_returns_none(self):
        params = {'type': 'invalid'}
        result = build_browse_url_if_possible(params)
        self.assertIsNone(result)

    def test_make_smart_link_uses_browse_url(self):
        params = {'type': 'ukpga', 'year': 2024}
        result = make_smart_link(params)
        self.assertEqual(result, '/ukpga/2024')

    def test_make_smart_link_with_title_filter_uses_browse_url(self):
        params = {'type': 'ukpga', 'title': 'housing'}
        result = make_smart_link(params)
        self.assertEqual(result, '/ukpga?title=housing')

    def test_make_smart_link_falls_back_to_search_for_disallowed_params(self):
        params = {'type': 'ukpga', 'pointInTime': '2024-01-01'}
        result = make_smart_link(params)
        self.assertTrue(result.startswith('/search/?'))
        self.assertIn('type=ukpga', result)
        self.assertIn('pointInTime=2024-01-01', result)

    def test_type_and_subject_initial(self):
        params = {'type': 'uksi', 'subject': 'a'}
        result = make_smart_link(params)
        self.assertEqual(result, '/uksi/a')

    def test_full_subject_heading_stays_in_query_string(self):
        params = {'type': 'ukpga', 'subject': 'animals'}
        result = build_browse_url_if_possible(params)
        self.assertEqual(result, '/ukpga?subject=animals')

    def test_year_and_full_subject_heading_stay_on_year_route(self):
        params = {'type': 'ukpga', 'year': 2024, 'subject': 'animals'}
        result = build_browse_url_if_possible(params)
        self.assertEqual(result, '/ukpga/2024?subject=animals')

    def test_build_browse_url_with_extent_name(self):
        params = {'type': 'ukpga', 'extent': ['E']}
        result = build_browse_url_if_possible(params)
        self.assertEqual(result, '/ukpga/england')

    def test_build_browse_url_with_exclusive_extent_name(self):
        params = {'type': 'ukpga', 'extent': ['E'], 'exclusiveExtent': True}
        result = build_browse_url_if_possible(params)
        self.assertEqual(result, '/ukpga/=england')

    def test_replace_param_removes_value_and_resets_pagination(self):
        params = {'type': 'ukpga', 'year': 2024, 'page': 3, 'pageSize': 50}
        result = replace_param_and_make_smart_link(params, 'year', None)
        self.assertEqual(result, '/ukpga')

    def test_build_browse_url_returns_none_for_out_of_range_year(self):
        params = {'type': 'ukpga', 'year': 999}
        result = build_browse_url_if_possible(params)
        self.assertIsNone(result)

    def test_make_smart_link_falls_back_to_search_when_year_invalid(self):
        params = {'type': 'ukpga', 'year': 999}
        result = make_smart_link(params)
        self.assertTrue(result.startswith('/search/?'))

    def test_extent_url_preserves_year_in_query_string(self):
        params = {'type': 'ukpga', 'extent': ['E'], 'year': 2024}
        result = build_browse_url_if_possible(params)
        self.assertEqual(result, '/ukpga/england?year=2024')

    def test_explicit_year_overrides_range(self):
        params = {'type': 'ukpga', 'startYear': 1900, 'endYear': 2000, 'year': 1950}
        result = build_browse_url_if_possible(params)
        self.assertEqual(result, '/ukpga/1950')


class TestBrowseExtentParsing(TestCase):
    @patch("lgu2.views.search.search_results_helper")
    def test_browse_extent_url_preserves_extent_code(self, mock_search_results_helper):
        request = RequestFactory().get("/ukpga/england")

        browse(request, type="ukpga", extent_segment="england")

        _, query_params = mock_search_results_helper.call_args.args
        self.assertEqual(query_params["extent"], ["E"])

    @patch("lgu2.views.search.search_results_helper")
    def test_browse_exclusive_extent_url_preserves_extent_code(self, mock_search_results_helper):
        request = RequestFactory().get("/ukpga/=england")

        browse(request, type="ukpga", extent_segment="=england")

        _, query_params = mock_search_results_helper.call_args.args
        self.assertEqual(query_params["extent"], ["E"])
        self.assertIs(query_params["exclusiveExtent"], True)

    @patch("lgu2.views.search.search_results_helper")
    def test_browse_extent_url_preserves_year_and_subject_from_query_string(self, mock_search_results_helper):
        request = RequestFactory().get("/ukpga/england", {"year": "2024", "subject": "a"})

        browse(request, type="ukpga", extent_segment="england")

        _, query_params = mock_search_results_helper.call_args.args
        self.assertEqual(query_params["year"], 2024)
        self.assertEqual(query_params["subject"], "a")
        self.assertEqual(query_params["extent"], ["E"])


class TestExtentUrlRouting(TestCase):
    def test_human_readable_extent_url_resolves_to_browse_extent(self):
        match = resolve("/ukpga/england")
        self.assertEqual(match.view_name, "browse-extent")

    def test_exclusive_human_readable_extent_url_resolves_to_browse_extent(self):
        match = resolve("/ukpga/=england")
        self.assertEqual(match.view_name, "browse-extent")


def _empty_search_response(**query):
    return {
        "meta": {
            "counts": {"total": 0, "byType": [], "byYear": [], "bySubjectInitial": []},
            "page": 1,
            "totalPages": 1,
            "query": query,
            "subjects": [],
        },
        "documents": [],
    }


class TestModifiedQueryLinksRendering(TestCase):
    @patch("lgu2.views.search.basic_search")
    def test_active_query_links_do_not_prepend_question_mark_to_full_urls(self, mock_basic_search):
        mock_basic_search.return_value = _empty_search_response(title="housing")

        response = self.client.get("/ukpga", {"title": "housing"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "href='/ukpga'")


class TestInvalidNumericSearchParams(TestCase):
    def test_extract_query_params_ignores_invalid_numeric_values(self):
        request_factory = RequestFactory()

        invalid_values = {
            "year": "abcd",
            "startYear": "19x0",
            "endYear": "20y0",
            "page": "oops",
            "pageSize": "ten",
        }

        request = request_factory.get("/search/", invalid_values)
        params = extract_query_params(request)

        for key in invalid_values:
            with self.subTest(key=key):
                self.assertNotIn(key, params)

    def test_search_view_returns_form_when_active_year_is_invalid(self):
        response = self.client.get("/search/", {
            "type": "ukpga",
            "specifi_years": "true",
            "year": "abcd",
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "new_theme/advance_search/full_search.html")

    def test_search_view_returns_form_when_active_year_range_is_invalid(self):
        response = self.client.get("/search/", {
            "type": "ukpga",
            "specifi_years": "false",
            "startYear": "abc",
            "endYear": "2000",
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "new_theme/advance_search/full_search.html")

    def test_search_view_ignores_invalid_inactive_year_field(self):
        response = self.client.get("/search/", {
            "type": "ukpga",
            "specifi_years": "false",
            "year": "abcd",
            "startYear": "1900",
            "endYear": "2000",
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/ukpga/1900-2000")

    def test_year_out_of_range_returns_form(self):
        response = self.client.get("/search/", {
            "type": "ukpga",
            "specifi_years": "true",
            "year": "999",
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "new_theme/advance_search/full_search.html")

    def test_year_too_large_returns_form(self):
        response = self.client.get("/search/", {
            "type": "ukpga",
            "specifi_years": "true",
            "year": "10000",
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "new_theme/advance_search/full_search.html")


class TestYearWithoutSpecifiYears(TestCase):
    """Result-page forms submit year as a hidden field without the specifi_years radio."""

    def test_year_is_parsed_when_specifi_years_absent(self):
        request = RequestFactory().get("/search/", {"year": "2024"})
        params = extract_query_params(request)
        self.assertEqual(params.get("year"), 2024)

    @patch("lgu2.views.search.basic_search")
    def test_year_sent_to_api_when_sort_prevents_redirect(self, mock_basic_search):
        mock_basic_search.return_value = _empty_search_response()
        self.client.get("/search/", {"type": "ukpga", "year": "2024", "sort": "title"})
        api_params = mock_basic_search.call_args.args[0]
        self.assertEqual(api_params.get("year"), 2024)
