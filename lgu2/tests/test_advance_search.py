from django.test import SimpleTestCase
from django.urls import reverse


class AdvanceSearchViewsTests(SimpleTestCase):

    def test_advance_search_view(self):
        response = self.client.get(reverse('advance-search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_theme/advance_search/full_search.html')

    def test_extent_search_view(self):
        response = self.client.get(reverse('extent-search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_theme/advance_search/geographic_extent.html')

    def test_point_in_time_search_view(self):
        response = self.client.get(reverse('point-in-time-search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_theme/advance_search/point_in_time.html')

    def test_draft_search_view(self):
        response = self.client.get(reverse('draft-search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_theme/advance_search/draft.html')

    def test_impact_search_view(self):
        response = self.client.get(reverse('impact-search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_theme/advance_search/impact.html')
