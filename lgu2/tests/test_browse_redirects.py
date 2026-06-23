"""The legacy /browse URLs 301 to their new-theme Explore equivalents.

Asserts the Location header directly rather than following the redirect, so the
tests don't depend on the upstream API that the target views call. Status 301
is asserted deliberately: these are permanent redirects, so the old /browse URLs
hand their search-engine standing to the new Explore pages.

The /cy variants lock in that the redirect respects the active locale prefix —
the routes live inside i18n_patterns, so a redirect that dropped the prefix
would strand Welsh users back on the English pages."""

from django.test import SimpleTestCase
from django.utils import translation


class BrowseRedirectTests(SimpleTestCase):

    def tearDown(self):
        # A GET to /cy/... leaves Welsh active on the thread-local; LocaleMiddleware
        # doesn't reset it, so without this it would leak into later tests' reverse().
        translation.deactivate()

    def test_browse_redirects_to_explore(self):
        response = self.client.get("/browse")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.headers["Location"], "/explore/")

    def test_browse_uk_redirects_to_uk_legislatures(self):
        response = self.client.get("/browse/uk")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.headers["Location"], "/explore/legislatures/uk")

    def test_welsh_browse_redirects_within_locale(self):
        response = self.client.get("/cy/browse")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.headers["Location"], "/cy/explore/")

    def test_welsh_browse_uk_redirects_within_locale(self):
        response = self.client.get("/cy/browse/uk")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.headers["Location"], "/cy/explore/legislatures/uk")
