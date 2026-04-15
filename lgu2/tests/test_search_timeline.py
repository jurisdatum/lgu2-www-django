from django.test import SimpleTestCase

from lgu2.util.cutoff import get_cutoff
from lgu2.views.search import group_by_decade


class SearchTimelineTests(SimpleTestCase):

    def test_ukia_has_cutoff_metadata(self):
        self.assertEqual(get_cutoff('ukia'), 2008)

    def test_group_by_decade_marks_post_cutoff_ukia_years_complete(self):
        grouped = group_by_decade([
            {'year': 2007, 'count': 1},
            {'year': 2008, 'count': 1},
            {'year': 2009, 'count': 2},
        ], 'ukia')

        years = {item['year']: item for item in grouped['2000-2009'] if not item.get('no_data')}

        self.assertFalse(years[2007]['complete'])
        self.assertTrue(years[2008]['complete'])
        self.assertTrue(years[2009]['complete'])
