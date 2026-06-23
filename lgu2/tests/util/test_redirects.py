from django.test import SimpleTestCase
from django.urls import reverse

from lgu2.util.redirects import should_redirect


def _fragment_meta(**overrides):
    meta = {
        "shortType": "ukpga",
        "year": 2024,
        "number": 1,
        "status": "final",
        "version": "2025-01-01",
        "fragmentInfo": {"href": "section/5", "label": "Section 5"},
    }
    meta.update(overrides)
    return meta


class ShouldRedirectFragmentTests(SimpleTestCase):
    """The fragment branch of should_redirect must carry the fragment's
    section into the redirect target, sourced from ``fragmentInfo['href']``
    (the replacement for the removed deprecated top-level ``fragment``)."""

    def test_final_status_redirects_to_versioned_url_with_section(self):
        response = should_redirect("fragment", "ukpga", None, None, _fragment_meta())
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse(
                "fragment-version",
                args=["ukpga", 2024, 1, "section/5", "2025-01-01"],
            ),
        )

    def test_section_tracks_fragment_info_href(self):
        # The redirect's section must follow fragmentInfo['href'] verbatim,
        # including multi-segment hrefs — this is the contract that replaced
        # the deprecated top-level ``fragment`` string.
        meta = _fragment_meta(fragmentInfo={"href": "schedule/2/paragraph/3"})
        response = should_redirect("fragment", "ukpga", None, None, meta)
        self.assertEqual(
            response.url,
            reverse(
                "fragment-version",
                args=["ukpga", 2024, 1, "schedule/2/paragraph/3", "2025-01-01"],
            ),
        )

    def test_section_carried_with_language(self):
        response = should_redirect("fragment", "ukpga", None, "welsh", _fragment_meta())
        self.assertEqual(
            response.url,
            reverse(
                "fragment-version-lang",
                args=["ukpga", 2024, 1, "section/5", "2025-01-01", "welsh"],
            ),
        )

    def test_type_canonicalisation_redirects_current_with_section(self):
        # Non-final, wrong requested type, no version -> redirect to the
        # canonical type at the current version, still carrying the section.
        meta = _fragment_meta(status="revised", shortType="uksi")
        response = should_redirect("fragment", "ukpga", None, None, meta)
        self.assertEqual(
            response.url,
            reverse("fragment", args=["uksi", 2024, 1, "section/5"]),
        )

    def test_versioned_request_on_canonical_type_does_not_redirect(self):
        response = should_redirect(
            "fragment", "ukpga", "2025-01-01", None, _fragment_meta()
        )
        self.assertIsNone(response)
