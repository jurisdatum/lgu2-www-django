from datetime import date

from django.test import SimpleTestCase
from django.urls import reverse

from lgu2.util.timeline import make_timeline_data


class DocumentTimelineTests(SimpleTestCase):

    def test_prospective_current_uses_versionless_link(self):
        meta = {
            'shortType': 'ukpga',
            'year': 2023,
            'number': 1,
            'versions': ['enacted', '2024-01-01', 'prospective'],
            'version': 'prospective',
            'date': date(2018, 6, 20),
        }

        timeline = make_timeline_data(meta, 'document')
        current = timeline['current']

        self.assertIsNotNone(current)
        self.assertIsNone(current['date'])
        self.assertEqual(
            current['link'],
            reverse('document', args=['ukpga', 2023, 1])
        )
        self.assertEqual(timeline['viewing'], current)

    def test_document_historical_version_selected(self):
        meta = {
            'shortType': 'ukpga',
            'year': 2023,
            'number': 1,
            'versions': ['enacted', '2022-01-01', '2024-01-01'],
            'version': '2022-01-01',
            'date': date(2018, 6, 20),
        }

        timeline = make_timeline_data(meta, 'document')
        viewing = timeline['viewing']

        self.assertEqual(viewing['label'], '2022-01-01')
        self.assertEqual(
            viewing['link'],
            reverse('document-version', args=['ukpga', 2023, 1, '2022-01-01'])
        )


class FragmentTimelineTests(SimpleTestCase):

    def test_prospective_fragment_uses_canonical_href(self):
        meta = {
            'shortType': 'ukpga',
            'year': 2023,
            'number': 1,
            'fragmentInfo': {'href': 'crossheading/final-provisions'},
            'versions': ['enacted', '2024-01-01', 'prospective'],
            'version': 'prospective',
            'date': date(2018, 6, 20),
        }

        timeline = make_timeline_data(meta, 'fragment')
        current = timeline['current']

        self.assertIsNone(current['date'])
        self.assertEqual(
            current['link'],
            reverse(
                'fragment',
                args=['ukpga', 2023, 1, 'crossheading/final-provisions']
            )
        )

    def test_fragment_historical_links_include_version(self):
        meta = {
            'shortType': 'ukpga',
            'year': 2023,
            'number': 1,
            'fragmentInfo': {'href': 'section/1'},
            'versions': ['enacted', '2022-01-01', '2024-01-01'],
            'version': '2024-01-01',
            'date': date(2018, 6, 20),
        }

        timeline = make_timeline_data(meta, 'fragment')
        historical = timeline['historical']

        self.assertEqual(len(historical), 1)
        entry = historical[0]
        self.assertEqual(entry['label'], '2022-01-01')
        self.assertEqual(
            entry['link'],
            reverse('fragment-version', args=['ukpga', 2023, 1, 'section/1', '2022-01-01'])
        )
        # The current (latest) version is shown without the version suffix.
        self.assertEqual(
            timeline['viewing']['link'],
            reverse('fragment', args=['ukpga', 2023, 1, 'section/1'])
        )


class TocTimelineTests(SimpleTestCase):

    def test_toc_timeline_includes_original_entry(self):
        meta = {
            'shortType': 'ukpga',
            'year': 2023,
            'number': 1,
            'versions': ['enacted', '2022-01-01'],
            'version': '2022-01-01',
            'date': date(2018, 6, 20),
        }

        timeline = make_timeline_data(meta, 'toc')
        original = timeline['original']

        self.assertIsNotNone(original)
        self.assertEqual(original['label'], 'enacted')
        self.assertEqual(
            original['link'],
            reverse('toc-version', args=['ukpga', 2023, 1, 'enacted'])
        )
