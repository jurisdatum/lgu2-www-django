from urllib.parse import parse_qs, urlencode, urlsplit
from unittest.mock import Mock, patch

from django.test import SimpleTestCase
from django.urls import reverse

from lgu2.views.changes.results import _make_nav


class ChangesRedirectTests(SimpleTestCase):
    def test_changes_intro_redirect_accepts_specific_year_without_year_choice(self):
        response = self.client.get(reverse('changes-intro'), {'affected-year': '1996'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            reverse('changes-affected', kwargs={'type': 'all', 'year': '1996'}),
        )

    def test_changes_intro_redirect_preserves_single_ended_year_ranges(self):
        response = self.client.get(
            reverse('changes-intro'),
            {'affected-year-choice': 'range', 'affected-start-year': '1990'},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response['Location'].startswith(reverse('changes-affected', kwargs={'type': 'all'}))
        )
        self.assertIn('affected-start-year=1990', response['Location'])

    def test_changes_intro_ignores_invalid_specific_year_instead_of_500ing(self):
        self.client.raise_request_exception = False

        response = self.client.get(
            reverse('changes-intro'),
            {'affected-year-choice': 'specific', 'affected-year': '19x0'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Changes to legislation')


class ChangesResultsNavTests(SimpleTestCase):
    def test_make_nav_returns_template_expected_link_objects(self):
        meta = {
            'page': 2,
            'pageSize': 20,
            'totalPages': 5,
            'startIndex': 21,
            'totalResults': 100,
            'updated': '2026-01-01T00:00:00Z',
        }

        nav = _make_nav(meta, '/changes/affected/uksi/2020')

        self.assertIsInstance(nav['first'], dict)
        self.assertIsInstance(nav['prev'], dict)
        self.assertIsInstance(nav['next'], dict)
        self.assertIsInstance(nav['last'], dict)
        self.assertTrue(nav['first']['link'])
        self.assertTrue(nav['prev']['link'])
        self.assertTrue(nav['next']['link'])
        self.assertTrue(nav['last']['link'])


class ChangesResultsFeedTests(SimpleTestCase):
    @patch('lgu2.views.changes.results.api.fetch')
    def test_results_rss_link_preserves_title_filters(self, mock_fetch):
        mock_fetch.return_value = {
            'meta': {
                'page': 1,
                'pageSize': 20,
                'totalPages': 1,
                'totalResults': 1,
            },
            'effects': [],
        }

        response = self.client.get(
            reverse('changes-affected', kwargs={'type': 'uksi'}),
            {'affected-title': 'Housing Act'},
        )

        expected_link = (
            reverse('changes-affected', kwargs={'type': 'uksi'})
            + '/data.feed?'
            + urlencode({'affected-title': 'Housing Act'})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'href="{expected_link}"')

    @patch('lgu2.api.effects.server.get')
    def test_feed_accepts_year_range_and_applied_filters(self, mock_get):
        mock_get.return_value = Mock(text='<feed/>')

        year_range_url = reverse(
            'changes-affected',
            kwargs={'type': 'uksi', 'year': '1996-1998', 'format': 'feed'},
        )
        applied_url = reverse(
            'changes-affected-applied',
            kwargs={'applied': 'applied', 'type': 'uksi', 'year': '1996', 'format': 'feed'},
        )

        for url in [year_range_url, applied_url]:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertIn('application/atom+xml', response['Content-Type'])

        self.assertEqual(mock_get.call_count, 2)
        queries = [parse_qs(urlsplit(call.args[0]).query) for call in mock_get.call_args_list]

        self.assertTrue(
            any(
                query.get('targetStartYear') == ['1996']
                and query.get('targetEndYear') == ['1998']
                for query in queries
            )
        )
        self.assertTrue(any(query.get('applied') == ['applied'] for query in queries))
        self.assertTrue(all(call.args[1] == 'application/atom+xml' for call in mock_get.call_args_list))
