from unittest.mock import patch

from django.test import SimpleTestCase
from django.urls import resolve, reverse

from lgu2.views import fragment


class SubprovisionRedirectTests(SimpleTestCase):

    def test_subprovision_data_urls_resolve_to_fragment_data_view(self):
        cases = [
            ('/ukpga/2024/1/section/1-2/data.json', 'fragment-data', {}),
            ('/ukpga/2024/1/section/1-2/2025-01-01/data.json', 'fragment-version-data',
             {'version': '2025-01-01'}),
            ('/ukpga/2024/1/section/1-2/english/data.json', 'fragment-lang-data',
             {'lang': 'english'}),
            ('/ukpga/2024/1/section/1-2/2025-01-01/english/data.json', 'fragment-version-lang-data',
             {'version': '2025-01-01', 'lang': 'english'}),
        ]

        for path, url_name, extra_kwargs in cases:
            with self.subTest(path=path):
                match = resolve(path)

                self.assertEqual(match.func, fragment.data)
                self.assertEqual(match.url_name, url_name)
                self.assertEqual(match.kwargs['section'], 'section/1-2')
                self.assertEqual(match.kwargs['format'], 'json')
                for key, value in extra_kwargs.items():
                    self.assertEqual(match.kwargs[key], value)

    @patch("lgu2.views.fragment.api.head")
    @patch("lgu2.views.fragment.api.get")
    def test_section_subprovision_redirects_to_parent_with_anchor(self, mock_get, mock_head):
        mock_head.return_value = 200

        response = self.client.get(reverse('fragment', args=['ukpga', 2024, 1, 'section/1-2']))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            reverse('fragment', args=['ukpga', 2024, 1, 'section/1']) + '#section-1-2',
        )
        mock_get.assert_not_called()

    @patch("lgu2.views.fragment.api.head")
    @patch("lgu2.views.fragment.api.get")
    def test_multi_level_subprovision_keeps_hyphenated_tail_in_anchor(self, mock_get, mock_head):
        mock_head.return_value = 200

        response = self.client.get(reverse('fragment', args=['ukpga', 2024, 1, 'section/1-2-a-i']))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            reverse('fragment', args=['ukpga', 2024, 1, 'section/1']) + '#section-1-2-a-i',
        )

    @patch("lgu2.views.fragment.api.head")
    @patch("lgu2.views.fragment.api.get")
    def test_nested_schedule_paragraph_subprovision(self, mock_get, mock_head):
        mock_head.return_value = 200

        response = self.client.get(reverse(
            'fragment', args=['ukpga', 2024, 1, 'schedule/1/paragraph/3-1']))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            reverse('fragment', args=['ukpga', 2024, 1, 'schedule/1/paragraph/3'])
            + '#schedule-1-paragraph-3-1',
        )

    @patch("lgu2.views.fragment.api.head")
    @patch("lgu2.views.fragment.api.get")
    def test_article_kind_with_letter_in_parent(self, mock_get, mock_head):
        mock_head.return_value = 200

        response = self.client.get(reverse('fragment', args=['uksi', 2024, 1, 'article/1A-3']))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            reverse('fragment', args=['uksi', 2024, 1, 'article/1A']) + '#article-1A-3',
        )

    @patch("lgu2.views.fragment.api.head")
    @patch("lgu2.views.fragment.api.get")
    def test_preserves_version_segment(self, mock_get, mock_head):
        mock_head.return_value = 200

        response = self.client.get(reverse(
            'fragment-version', args=['ukpga', 2024, 1, 'section/1-2', '2025-01-01']))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            reverse('fragment-version', args=['ukpga', 2024, 1, 'section/1', '2025-01-01']) + '#section-1-2',
        )

    @patch("lgu2.views.fragment.api.head")
    @patch("lgu2.views.fragment.api.get")
    def test_preserves_language_segment(self, mock_get, mock_head):
        mock_head.return_value = 200

        response = self.client.get(reverse(
            'fragment-lang', args=['ukpga', 2024, 1, 'section/1-2', 'english']))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            reverse('fragment-lang', args=['ukpga', 2024, 1, 'section/1', 'english']) + '#section-1-2',
        )

    @patch("lgu2.views.fragment.api.head")
    @patch("lgu2.views.fragment.api.get")
    def test_preserves_version_and_language(self, mock_get, mock_head):
        mock_head.return_value = 200

        response = self.client.get(reverse(
            'fragment-version-lang',
            args=['ukpga', 2024, 1, 'section/1-2', '2025-01-01', 'english']))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            reverse('fragment-version-lang',
                    args=['ukpga', 2024, 1, 'section/1', '2025-01-01', 'english']) + '#section-1-2',
        )

    @patch("lgu2.views.fragment.api.head")
    @patch("lgu2.views.fragment.api.get")
    def test_head_404_returns_404(self, mock_get, mock_head):
        mock_head.return_value = 404

        response = self.client.get(reverse('fragment', args=['ukpga', 2024, 1, 'section/1-999']))

        self.assertEqual(response.status_code, 404)
        mock_get.assert_not_called()

    @patch("lgu2.views.fragment.api.head")
    @patch("lgu2.views.fragment.api.get")
    def test_non_subprovision_shape_falls_through(self, mock_get, mock_head):
        # section/1 has no hyphen → normal fragment request
        mock_get.return_value = {'error': 'ignored', 'meta': {}}

        self.client.get(reverse('fragment', args=['ukpga', 2024, 1, 'section/1']))

        mock_head.assert_not_called()
        mock_get.assert_called_once()

    @patch("lgu2.views.fragment.api.head")
    @patch("lgu2.views.fragment.api.get")
    def test_crossheading_with_hyphenated_title_is_excluded(self, mock_get, mock_head):
        # section/1/crossheading/something-or-other: 'crossheading' is not in
        # _SUBPROVISION_KINDS, so _split_subprovision returns None immediately.
        mock_get.return_value = {'error': 'ignored', 'meta': {}}

        self.client.get(reverse(
            'fragment', args=['ukpga', 2024, 1, 'section/1/crossheading/something-or-other']))

        mock_head.assert_not_called()
        mock_get.assert_called_once()

    @patch("lgu2.views.fragment.api.head")
    @patch("lgu2.views.fragment.api.get")
    def test_head_non_200_non_404_falls_through(self, mock_get, mock_head):
        # A 500 (or any other status) should not short-circuit; the main view
        # will make its own call to the API and handle the error itself.
        mock_head.return_value = 500
        mock_get.return_value = {'error': 'ignored', 'meta': {}}

        response = self.client.get(reverse('fragment', args=['ukpga', 2024, 1, 'section/1-2']))

        self.assertEqual(response.status_code, 404)  # view falls through to normal handling; 404 here is from the stub API response, not the redirect logic
        mock_head.assert_called_once()
        mock_get.assert_called_once()

    @patch("lgu2.views.fragment.api.head")
    @patch("lgu2.views.fragment.api.get")
    def test_each_subprovision_kind_is_detected(self, mock_get, mock_head):
        mock_head.return_value = 200

        for kind in ('section', 'article', 'paragraph', 'rule', 'regulation'):
            with self.subTest(kind=kind):
                response = self.client.get(reverse('fragment', args=['ukpga', 2024, 1, f'{kind}/1-2']))
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response['Location'].endswith(f'#{kind}-1-2'))
