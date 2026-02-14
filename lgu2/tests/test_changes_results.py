from urllib.parse import parse_qs, urlsplit
from unittest.mock import Mock, patch

from django.test import SimpleTestCase
from django.urls import reverse

from lgu2.views.changes.results import _make_nav


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
