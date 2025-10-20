from datetime import datetime, timezone

from django.test import SimpleTestCase
from django.urls import reverse

from lgu2.util.links import (
    make_contents_link_for_list_entry,
    make_contents_link,
    make_fragment_link,
    make_document_link,
)


def _base_doc(version: str = "enacted") -> dict:
    now = datetime.now(timezone.utc)
    return {
        "id": "ukpga/2023/1",
        "longType": "UnitedKingdomPublicGeneralAct",
        "year": 2023,
        "number": 1,
        "altNumbers": [],
        "cite": "2023 c.1",
        "title": "Finance Act 2023",
        "published": now,
        "updated": now,
        "version": version,
        "formats": ["xml"],
    }


class MakeContentsLinkForListEntryTests(SimpleTestCase):

    def test_first_version_uses_version_url(self):
        doc = _base_doc("enacted")
        expected = reverse("toc-version", args=["ukpga", 2023, 1, "enacted"])
        self.assertEqual(make_contents_link_for_list_entry(doc), expected)

    def test_revision_uses_toc_url(self):
        doc = _base_doc("2024-01-01")
        expected = reverse("toc", args=["ukpga", 2023, 1])
        self.assertEqual(make_contents_link_for_list_entry(doc), expected)

    def test_correction_slip_points_to_parent_document(self):
        doc = _base_doc("2024-01-01")
        doc["id"] = "uksi/2024/100.pdf"
        doc["longType"] = "UnitedKingdomStatutoryInstrument"
        doc["year"] = 2024
        doc["number"] = 100
        expected = reverse("toc", args=["uksi", 2024, 100])
        self.assertEqual(make_contents_link_for_list_entry(doc), expected)


class MakeContentsLinkTests(SimpleTestCase):

    def test_without_version_or_language(self):
        self.assertEqual(
            make_contents_link("ukpga", 2023, 1, None, None),
            reverse("toc", args=["ukpga", 2023, 1]),
        )

    def test_with_version(self):
        self.assertEqual(
            make_contents_link("ukpga", 2023, 1, "enacted", None),
            reverse("toc-version", args=["ukpga", 2023, 1, "enacted"]),
        )

    def test_with_language(self):
        self.assertEqual(
            make_contents_link("ukpga", 2023, 1, None, "welsh"),
            reverse("toc-lang", args=["ukpga", 2023, 1, "welsh"]),
        )

    def test_with_version_and_language(self):
        self.assertEqual(
            make_contents_link("ukpga", 2023, 1, "enacted", "english"),
            reverse("toc-version-lang", args=["ukpga", 2023, 1, "enacted", "english"]),
        )


class MakeFragmentLinkTests(SimpleTestCase):
    """
    Tests for fragment link generation.

    Prior to October 2025, fragment links were constructed by replacing all
    dashes with slashes (e.g., 'crossheading-final-provisions' became
    'crossheading/final/provisions'). This broke crossheading links because
    dashes within multi-word titles should be preserved.

    The API now provides canonical fragment identifiers (href values) that
    include the correct structure. These tests verify we use those canonical
    values instead of performing dash replacement.
    """

    def test_fragment_without_version_or_language(self):
        fragment = "section/1"
        self.assertEqual(
            make_fragment_link("ukpga", 2023, 1, fragment, None, None),
            reverse("fragment", args=["ukpga", 2023, 1, fragment]),
        )

    def test_crossheading_preserves_dashes(self):
        fragment = "crossheading/final-provisions"
        self.assertEqual(
            make_fragment_link("ukpga", 2023, 1, fragment, None, None),
            reverse("fragment", args=["ukpga", 2023, 1, fragment]),
        )

    def test_crossheading_with_multiword_title(self):
        fragment = "crossheading/some-multi-word-title"
        self.assertEqual(
            make_fragment_link("ukpga", 2023, 1, fragment, None, None),
            reverse("fragment", args=["ukpga", 2023, 1, fragment]),
        )

    def test_schedule_fragment_with_multiple_parts(self):
        fragment = "schedule/1/paragraph/3"
        self.assertEqual(
            make_fragment_link("ukpga", 2023, 1, fragment, None, None),
            reverse("fragment", args=["ukpga", 2023, 1, fragment]),
        )

    def test_fragment_with_version(self):
        fragment = "section/1"
        self.assertEqual(
            make_fragment_link("ukpga", 2023, 1, fragment, "2024-01-01", None),
            reverse("fragment-version", args=["ukpga", 2023, 1, fragment, "2024-01-01"]),
        )

    def test_fragment_with_language(self):
        fragment = "section/1"
        self.assertEqual(
            make_fragment_link("ukpga", 2023, 1, fragment, None, "english"),
            reverse("fragment-lang", args=["ukpga", 2023, 1, fragment, "english"]),
        )

    def test_fragment_with_version_and_language(self):
        fragment = "section/1"
        self.assertEqual(
            make_fragment_link("ukpga", 2023, 1, fragment, "2024-01-01", "welsh"),
            reverse(
                "fragment-version-lang",
                args=["ukpga", 2023, 1, fragment, "2024-01-01", "welsh"],
            ),
        )


class MakeDocumentLinkTests(SimpleTestCase):

    def test_document_without_version_or_language(self):
        self.assertEqual(
            make_document_link("ukpga", 2023, 1, None, None),
            reverse("document", args=["ukpga", 2023, 1]),
        )

    def test_document_with_version(self):
        self.assertEqual(
            make_document_link("ukpga", 2023, 1, "enacted", None),
            reverse("document-version", args=["ukpga", 2023, 1, "enacted"]),
        )

    def test_document_with_language(self):
        self.assertEqual(
            make_document_link("ukpga", 2023, 1, None, "english"),
            reverse("document-lang", args=["ukpga", 2023, 1, "english"]),
        )

    def test_document_with_version_and_language(self):
        self.assertEqual(
            make_document_link("ukpga", 2023, 1, "enacted", "welsh"),
            reverse(
                "document-version-lang",
                args=["ukpga", 2023, 1, "enacted", "welsh"],
            ),
        )
