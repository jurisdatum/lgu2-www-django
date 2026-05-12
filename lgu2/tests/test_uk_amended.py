from unittest.mock import patch

from django.test import RequestFactory, TestCase

from lgu2.util.global_redirect import build_browse_url_if_possible
from lgu2.util.search_params import from_api_response, to_api_request
from lgu2.util.url_params import to_ui_params
from lgu2.views.search import (
    enforce_uk_amended_invariant,
    extract_query_params,
    make_smart_link,
    replace_param_and_make_smart_link,
)


def _eu_search_response(query=None):
    """Build a minimal API response with three EU byType rows (parent + true + false)."""
    return {
        'meta': {
            'page': 1,
            'totalPages': 1,
            'query': query or {},
            'subjects': [],
            'counts': {
                'total': 0,
                'byType': [
                    {'type': 'EuropeanUnionRegulation', 'count': 1234},
                    {'type': 'EuropeanUnionRegulation', 'count': 47, 'ukAmended': True},
                    {'type': 'EuropeanUnionRegulation', 'count': 1187, 'ukAmended': False},
                ],
                'byYear': [],
                'bySubjectInitial': [],
                'byStage': [],
                'byDepartment': [],
            },
        },
        'documents': [],
    }


class TestBuildBrowseUrlUkAmended(TestCase):
    """ukAmended is preserved on browse URLs as the lowercase ukamended key."""

    def test_eu_type_with_uk_amended_true(self):
        result = build_browse_url_if_possible({'type': 'eur', 'ukAmended': True})
        self.assertEqual(result, '/eur?ukamended=true')

    def test_eu_type_with_uk_amended_false(self):
        result = build_browse_url_if_possible({'type': 'eur', 'ukAmended': False})
        self.assertEqual(result, '/eur?ukamended=false')

    def test_eu_type_with_year_and_uk_amended(self):
        result = build_browse_url_if_possible({'type': 'eur', 'year': 2024, 'ukAmended': False})
        self.assertEqual(result, '/eur/2024?ukamended=false')

    def test_uk_amended_uses_lowercase_value_not_python_repr(self):
        result = build_browse_url_if_possible({'type': 'eur', 'ukAmended': True})
        self.assertNotIn('True', result)
        self.assertNotIn('ukAmended', result)


class TestToApiRequest(TestCase):
    def test_renames_text_to_q(self):
        out = to_api_request({'text': 'fire'})
        self.assertEqual(out, {'q': 'fire'})
        self.assertNotIn('text', out)

    def test_uk_amended_keeps_camelcase(self):
        out = to_api_request({'type': 'eur', 'ukAmended': True})
        self.assertEqual(out, {'type': 'eur', 'ukAmended': True})

    def test_does_not_mutate_input(self):
        params = {'text': 'fire', 'type': 'ukpga'}
        to_api_request(params)
        self.assertEqual(params, {'text': 'fire', 'type': 'ukpga'})


class TestFromApiResponse(TestCase):
    def test_renames_meta_query_q_to_text(self):
        api = {'meta': {'query': {'q': 'fire', 'sort': 'title'}}, 'documents': []}
        out = from_api_response(api)
        self.assertEqual(out['meta']['query'], {'text': 'fire', 'sort': 'title'})

    def test_does_not_mutate_input(self):
        api = {'meta': {'query': {'q': 'fire'}}, 'documents': []}
        from_api_response(api)
        self.assertEqual(api['meta']['query'], {'q': 'fire'})

    def test_passes_through_when_no_q(self):
        api = {'meta': {'query': {'sort': 'title'}}, 'documents': []}
        out = from_api_response(api)
        self.assertEqual(out['meta']['query'], {'sort': 'title'})

    def test_handles_missing_query(self):
        api = {'meta': {}, 'documents': []}
        out = from_api_response(api)
        self.assertEqual(out['meta'], {})


class TestToUiParams(TestCase):
    def test_renames_uk_amended_to_lowercase(self):
        out = to_ui_params({'type': 'eur', 'ukAmended': False})
        self.assertEqual(out, {'type': 'eur', 'ukamended': 'false'})

    def test_other_camelcase_keys_not_renamed(self):
        out = to_ui_params({'startYear': 1900, 'pageSize': 20})
        self.assertEqual(out, {'startYear': 1900, 'pageSize': 20})

    def test_lowercases_booleans(self):
        out = to_ui_params({'ukAmended': True})
        self.assertEqual(out, {'ukamended': 'true'})


class TestExtractQueryParamsUkAmended(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_lowercase_true_is_parsed_as_internal_camelcase_key(self):
        request = self.factory.get('/search/?ukamended=true')
        params = extract_query_params(request)
        self.assertIs(params.get('ukAmended'), True)
        self.assertNotIn('ukamended', params)

    def test_lowercase_false_is_parsed(self):
        request = self.factory.get('/search/?ukamended=false')
        params = extract_query_params(request)
        self.assertIs(params.get('ukAmended'), False)

    def test_mixed_case_value_is_accepted(self):
        request = self.factory.get('/search/?ukamended=TRUE')
        params = extract_query_params(request)
        self.assertIs(params.get('ukAmended'), True)

    def test_other_values_are_dropped(self):
        for bad in ('1', '0', 'yes', 'no', 'maybe', ''):
            with self.subTest(value=bad):
                request = self.factory.get('/search/?ukamended=' + bad)
                params = extract_query_params(request)
                self.assertNotIn('ukAmended', params)


class TestEnforceUkAmendedInvariant(TestCase):
    def test_eu_atomic_type_preserves_uk_amended(self):
        params = {'type': 'eur', 'ukAmended': True}
        enforce_uk_amended_invariant(params)
        self.assertIs(params.get('ukAmended'), True)

    def test_non_eu_type_strips_uk_amended(self):
        params = {'type': 'ukpga', 'ukAmended': True}
        enforce_uk_amended_invariant(params)
        self.assertNotIn('ukAmended', params)

    def test_no_type_strips_uk_amended(self):
        params = {'ukAmended': True}
        enforce_uk_amended_invariant(params)
        self.assertNotIn('ukAmended', params)

    def test_compound_set_with_any_eu_member_preserves(self):
        params = {'type': ['eur', 'ukpga'], 'ukAmended': True}
        enforce_uk_amended_invariant(params)
        self.assertIs(params.get('ukAmended'), True)

    def test_compound_set_all_non_eu_strips(self):
        params = {'type': ['ukpga', 'uksi'], 'ukAmended': True}
        enforce_uk_amended_invariant(params)
        self.assertNotIn('ukAmended', params)

    def test_eu_origin_aggregate_token_preserves(self):
        params = {'type': ['eu-origin'], 'ukAmended': True}
        enforce_uk_amended_invariant(params)
        self.assertIs(params.get('ukAmended'), True)

    def test_eu_aggregate_token_preserves(self):
        params = {'type': ['eu'], 'ukAmended': True}
        enforce_uk_amended_invariant(params)
        self.assertIs(params.get('ukAmended'), True)

    def test_other_eu_atomic_types_preserve(self):
        for t in ('eudn', 'eudr', 'eut'):
            with self.subTest(type=t):
                params = {'type': t, 'ukAmended': False}
                enforce_uk_amended_invariant(params)
                self.assertIs(params.get('ukAmended'), False)


class TestReplaceParamAndMakeSmartLink(TestCase):
    """Switching or clearing type re-applies the EU-type invariant."""

    def test_switch_eu_to_non_eu_strips_uk_amended(self):
        url = replace_param_and_make_smart_link(
            {'type': 'eur', 'ukAmended': True}, 'type', 'ukpga'
        )
        self.assertNotIn('ukAmended', url)
        self.assertNotIn('ukamended', url)

    def test_clear_type_strips_uk_amended(self):
        url = replace_param_and_make_smart_link(
            {'type': 'eur', 'ukAmended': True}, 'type', None
        )
        self.assertNotIn('ukAmended', url)
        self.assertNotIn('ukamended', url)

    def test_clear_uk_amended_preserves_eu_type(self):
        url = replace_param_and_make_smart_link(
            {'type': 'eur', 'ukAmended': True}, 'ukAmended', None
        )
        self.assertEqual(url, '/eur')

    def test_switch_eu_to_other_eu_keeps_uk_amended(self):
        url = replace_param_and_make_smart_link(
            {'type': 'eur', 'ukAmended': True}, 'type', 'eudr'
        )
        self.assertEqual(url, '/eudr?ukamended=true')


class TestBrowseViewPathThenInvariant(TestCase):
    """Path-derived type is honoured by the invariant; non-EU paths strip ukAmended."""

    @patch('lgu2.views.search.basic_search')
    def test_eu_path_with_uk_amended_query_preserves_filter(self, mock_basic_search):
        mock_basic_search.return_value = _eu_search_response(query={'type': 'eur', 'ukAmended': True})
        response = self.client.get('/eur', {'ukamended': 'true'})
        self.assertEqual(response.status_code, 200)
        api_params = mock_basic_search.call_args.args[0]
        self.assertIs(api_params.get('ukAmended'), True)

    @patch('lgu2.views.search.basic_search')
    def test_non_eu_path_with_uk_amended_query_strips_filter(self, mock_basic_search):
        mock_basic_search.return_value = {
            'meta': {
                'page': 1, 'totalPages': 1, 'query': {}, 'subjects': [],
                'counts': {'total': 0, 'byType': [], 'byYear': [],
                           'bySubjectInitial': [], 'byStage': [], 'byDepartment': []},
            },
            'documents': [],
        }
        response = self.client.get('/ukpga', {'ukamended': 'true'})
        self.assertEqual(response.status_code, 200)
        api_params = mock_basic_search.call_args.args[0]
        self.assertNotIn('ukAmended', api_params)


class TestSearchRedirectAppliesInvariantEarly(TestCase):
    """A /search?type=ukpga&ukamended=true URL should canonicalise to /ukpga, not /ukpga?ukamended=true."""

    @patch('lgu2.views.search.basic_search')
    def test_redirect_drops_orphan_uk_amended(self, mock_basic_search):
        response = self.client.get('/search/', {'type': 'ukpga', 'ukamended': 'true'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/ukpga')


class TestApiClientForwardsCamelCase(TestCase):
    @patch('lgu2.api.search.requests.get')
    def test_api_client_keeps_camelcase_ukAmended(self, mock_get):
        mock_get.return_value.json.return_value = {
            'meta': {'updated': '2024-01-01T00:00:00Z'},
            'documents': [],
        }
        mock_get.return_value.raise_for_status.return_value = None
        from lgu2.api.search import basic_search
        basic_search({'type': 'eur', 'ukAmended': True})
        params_arg = mock_get.call_args.kwargs['params']
        # API forwarding keeps camelCase ukAmended; bool is wire-coerced
        # to lowercase string inside basic_search.
        self.assertIn('ukAmended', params_arg)
        self.assertNotIn('ukamended', params_arg)
        self.assertEqual(params_arg['ukAmended'], 'true')


class TestTypeFilterGroups(TestCase):
    @patch('lgu2.views.search.basic_search')
    def test_eu_type_groups_into_parent_with_two_sub_entries(self, mock_basic_search):
        mock_basic_search.return_value = _eu_search_response(query={'type': 'eur'})
        response = self.client.get('/eur')
        self.assertEqual(response.status_code, 200)
        groups = response.context['type_filter_groups']
        self.assertEqual(len(groups), 1)
        group = groups[0]
        self.assertEqual(group['base_type'], 'eur')
        self.assertEqual(group['parent']['count'], 1234)
        self.assertEqual(len(group['sub_entries']), 2)
        # Sorted Amended → Not amended
        self.assertIs(group['sub_entries'][0]['ukAmended'], True)
        self.assertIs(group['sub_entries'][1]['ukAmended'], False)
        self.assertEqual(group['sub_entries'][0]['count'], 47)
        self.assertEqual(group['sub_entries'][1]['count'], 1187)

    @patch('lgu2.views.search.basic_search')
    def test_unqualified_only_groups_have_no_sub_entries(self, mock_basic_search):
        mock_basic_search.return_value = {
            'meta': {
                'page': 1, 'totalPages': 1, 'query': {'type': 'ukpga'}, 'subjects': [],
                'counts': {
                    'total': 1,
                    'byType': [{'type': 'UnitedKingdomPublicGeneralAct', 'count': 1}],
                    'byYear': [], 'bySubjectInitial': [], 'byStage': [], 'byDepartment': [],
                },
            },
            'documents': [],
        }
        response = self.client.get('/ukpga')
        groups = response.context['type_filter_groups']
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]['sub_entries'], [])

    @patch('lgu2.views.search.basic_search')
    def test_groups_without_parent_row_are_dropped(self, mock_basic_search):
        # If the API misbehaves and returns only qualified rows for a type,
        # the group is omitted entirely rather than rendered with an empty
        # parent link — Django trusts API counts and won't synthesise one.
        mock_basic_search.return_value = {
            'meta': {
                'page': 1, 'totalPages': 1, 'query': {}, 'subjects': [],
                'counts': {
                    'total': 0,
                    'byType': [
                        {'type': 'EuropeanUnionRegulation', 'count': 47, 'ukAmended': True},
                        {'type': 'EuropeanUnionRegulation', 'count': 1187, 'ukAmended': False},
                    ],
                    'byYear': [], 'bySubjectInitial': [], 'byStage': [], 'byDepartment': [],
                },
            },
            'documents': [],
        }
        response = self.client.get('/eur')
        groups = response.context['type_filter_groups']
        self.assertEqual(groups, [])

    @patch('lgu2.views.search.basic_search')
    def test_no_synthesised_all_sub_entry(self, mock_basic_search):
        mock_basic_search.return_value = _eu_search_response()
        response = self.client.get('/eur')
        groups = response.context['type_filter_groups']
        self.assertEqual(len(groups[0]['sub_entries']), 2)

    @patch('lgu2.views.search.basic_search')
    def test_group_collapses_to_matching_sub_entry_when_filtered(self, mock_basic_search):
        # When ukAmended is active, the API can't return reliable parent or
        # opposite-sub-entry counts. The group collapses to a single row
        # showing only the matching sub-entry, promoted into the parent slot.
        mock_basic_search.return_value = _eu_search_response(query={'type': 'eur', 'ukAmended': True})
        response = self.client.get('/eur', {'ukamended': 'true'})
        group = response.context['type_filter_groups'][0]
        self.assertEqual(group['sub_entries'], [])
        self.assertEqual(group['parent']['count'], 47)
        self.assertTrue(group['parent']['current'])
        self.assertIn('that are amended by the UK', group['label'])


class TestActiveFiltersChipModel(TestCase):
    @patch('lgu2.views.search.basic_search')
    def test_uk_amended_chip_built_from_query_params_not_meta_echo(self, mock_basic_search):
        # API echo deliberately omits ukAmended; the chip should still appear
        # because it comes from query_params, not meta.query.
        response_data = _eu_search_response(query={'type': 'eur'})
        mock_basic_search.return_value = response_data
        response = self.client.get('/eur', {'ukamended': 'true'})
        chips = response.context['active_filters']
        chip_keys = [c['key'] for c in chips]
        self.assertIn('ukAmended', chip_keys)
        chip = next(c for c in chips if c['key'] == 'ukAmended')
        self.assertEqual(chip['label'], 'Amended by UK legislation')
        self.assertIsNone(chip['value'])

    @patch('lgu2.views.search.basic_search')
    def test_uk_amended_chip_remove_link_clears_only_that_param(self, mock_basic_search):
        mock_basic_search.return_value = _eu_search_response(query={'type': 'eur'})
        response = self.client.get('/eur', {'ukamended': 'false'})
        chips = response.context['active_filters']
        chip = next(c for c in chips if c['key'] == 'ukAmended')
        self.assertEqual(chip['remove_link'], '/eur')

    @patch('lgu2.views.search.basic_search')
    def test_not_amended_chip_uses_correct_label(self, mock_basic_search):
        mock_basic_search.return_value = _eu_search_response(query={'type': 'eur'})
        response = self.client.get('/eur', {'ukamended': 'false'})
        chips = response.context['active_filters']
        chip = next(c for c in chips if c['key'] == 'ukAmended')
        self.assertEqual(chip['label'], 'Not amended by UK legislation')


class TestYearRangeChipRemoveLink(TestCase):
    """A year range arrives as separate startYear+endYear chips. Removing
    either chip must clear the whole range, not leave a half-range behind."""

    @patch('lgu2.views.search.basic_search')
    def test_year_range_chips_remove_link_clears_whole_range(self, mock_basic_search):
        mock_basic_search.return_value = {
            'meta': {
                'page': 1, 'totalPages': 1,
                'query': {'type': 'ukpga', 'startYear': 1900, 'endYear': 2000},
                'subjects': [],
                'counts': {
                    'total': 0, 'byType': [], 'byYear': [],
                    'bySubjectInitial': [], 'byStage': [], 'byDepartment': [],
                },
            },
            'documents': [],
        }
        response = self.client.get('/ukpga/1900-2000')
        chips = {c['key']: c for c in response.context['active_filters']}
        self.assertEqual(chips['startYear']['remove_link'], '/ukpga')
        self.assertEqual(chips['endYear']['remove_link'], '/ukpga')


class TestExtentRemoveLinkIsClean(TestCase):
    """Removing `extent` should also drop the now-dangling exclusiveExtent
    flag — normalize_params_for_browse() handles this implicitly. Lock it in."""

    def test_remove_extent_drops_exclusive_flag(self):
        link = replace_param_and_make_smart_link(
            {'type': 'ukpga', 'extent': ['E'], 'exclusiveExtent': True},
            'extent',
            None,
        )
        self.assertEqual(link, '/ukpga')


class TestAllLegislationTypesLinkClearsUkAmended(TestCase):
    @patch('lgu2.views.search.basic_search')
    def test_modified_query_links_type_clears_uk_amended(self, mock_basic_search):
        mock_basic_search.return_value = _eu_search_response(query={'type': 'eur', 'ukAmended': True})
        response = self.client.get('/eur', {'ukamended': 'true'})
        links = response.context['modified_query_links']
        # Clearing type strips ukAmended via the invariant.
        self.assertEqual(links['type'], '/search/')


class TestHiddenFormInputsUseUiKey(TestCase):
    """The sort and pageSize forms re-submit to /search/, which only reads
    the lowercase `ukamended` key. Hidden inputs must therefore use the UI
    spelling, not the internal camelCase `ukAmended`."""

    @patch('lgu2.views.search.basic_search')
    def test_hidden_inputs_emit_lowercase_ukamended(self, mock_basic_search):
        mock_basic_search.return_value = _eu_search_response(query={'type': 'eur', 'ukAmended': True})
        response = self.client.get('/eur', {'ukamended': 'true'})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('name="ukamended"', content)
        self.assertNotIn('name="ukAmended"', content)
        # Boolean values must be lowercased too — Python repr "True" is wrong.
        self.assertIn('value="true"', content)


class TestMakeSmartLinkUiSerialization(TestCase):
    def test_smart_link_emits_lowercase_ukamended_when_falling_back_to_search(self):
        url = make_smart_link({'type': 'eur', 'ukAmended': True, 'sort': 'title'})
        self.assertIn('ukamended=true', url)
        self.assertNotIn('ukAmended', url)
        self.assertNotIn('True', url)
