from django.test import SimpleTestCase

from lgu2.views.changes.redirect import redirect_with_query


class TestRedirectWithQuery(SimpleTestCase):
    def test_no_query_kwargs_produces_url_without_question_mark(self):
        response = redirect_with_query(
            "changes-applied-only", path_kwargs={"applied": "applied"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/changes/applied")

    def test_empty_query_kwargs_produces_url_without_question_mark(self):
        # Regression guard for reverse(query=...) refactor: passing {} would
        # leave a bare "?" on the URL without the `or None` guard.
        response = redirect_with_query(
            "changes-applied-only",
            path_kwargs={"applied": "applied"},
            query_kwargs={},
        )
        self.assertEqual(response["Location"], "/changes/applied")

    def test_query_kwargs_are_appended_as_query_string(self):
        response = redirect_with_query(
            "changes-applied-only",
            path_kwargs={"applied": "applied"},
            query_kwargs={"affected-title": "housing"},
        )
        self.assertEqual(
            response["Location"], "/changes/applied?affected-title=housing"
        )
