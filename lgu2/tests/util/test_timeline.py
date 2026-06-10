from datetime import date

from django.test import SimpleTestCase
from django.template.loader import render_to_string
from django.urls import reverse

from lgu2.util.timeline import make_timeline_data


class DocumentTimelineTests(SimpleTestCase):

    def test_prospective_current_uses_versionless_link(self):
        meta = {
            "shortType": "ukpga",
            "year": 2023,
            "number": 1,
            "versions": ["enacted", "2024-01-01", "prospective"],
            "version": "prospective",
            "date": date(2018, 6, 20),
        }

        timeline = make_timeline_data(meta, "document")
        current = timeline["current"]

        self.assertIsNone(current["date"])
        self.assertEqual(current["link"], reverse("document", args=["ukpga", 2023, 1]))
        self.assertEqual(timeline["viewing"], current)

    def test_document_historical_version_selected(self):
        meta = {
            "shortType": "ukpga",
            "year": 2023,
            "number": 1,
            "versions": ["enacted", "2022-01-01", "2024-01-01"],
            "version": "2022-01-01",
            "date": date(2018, 6, 20),
        }

        timeline = make_timeline_data(meta, "document")
        viewing = timeline["viewing"]

        self.assertEqual(viewing["label"], "2022-01-01")
        self.assertEqual(
            viewing["link"],
            reverse("document-version", args=["ukpga", 2023, 1, "2022-01-01"]),
        )


class FragmentTimelineTests(SimpleTestCase):

    def test_prospective_fragment_uses_canonical_href(self):
        meta = {
            "shortType": "ukpga",
            "year": 2023,
            "number": 1,
            "fragmentInfo": {"href": "crossheading/final-provisions"},
            "versions": ["enacted", "2024-01-01", "prospective"],
            "version": "prospective",
            "date": date(2018, 6, 20),
        }

        timeline = make_timeline_data(meta, "fragment")
        current = timeline["current"]

        self.assertIsNone(current["date"])
        self.assertEqual(
            current["link"],
            reverse(
                "fragment", args=["ukpga", 2023, 1, "crossheading/final-provisions"]
            ),
        )

    def test_fragment_historical_links_include_version(self):
        meta = {
            "shortType": "ukpga",
            "year": 2023,
            "number": 1,
            "fragmentInfo": {"href": "section/1"},
            "versions": ["enacted", "2022-01-01", "2024-01-01"],
            "version": "2024-01-01",
            "date": date(2018, 6, 20),
        }

        timeline = make_timeline_data(meta, "fragment")
        entries = timeline["entries"]

        self.assertEqual(len(entries), 1)
        entry = entries[0]
        self.assertEqual(entry["label"], "2022-01-01")
        self.assertEqual(
            entry["link"],
            reverse(
                "fragment-version", args=["ukpga", 2023, 1, "section/1", "2022-01-01"]
            ),
        )
        self.assertEqual(
            timeline["viewing"]["link"],
            reverse("fragment", args=["ukpga", 2023, 1, "section/1"]),
        )


class TimelineVisibilityTests(SimpleTestCase):

    def test_single_enacted_version(self):
        meta = {
            "shortType": "ukpga",
            "year": 2023,
            "number": 1,
            "versions": ["enacted"],
            "version": "enacted",
            "date": date(2018, 6, 20),
        }
        timeline = make_timeline_data(meta, "document")
        self.assertIsNotNone(timeline)
        self.assertEqual(timeline["current"]["label"], "enacted")
        self.assertEqual(timeline["entries"], [])
        self.assertTrue(timeline["single_version"])

    def test_multiple_versions_viewing_enacted_returns_none(self):
        meta = {
            "shortType": "ukpga",
            "year": 2023,
            "number": 1,
            "versions": ["enacted", "2024-01-01"],
            "version": "enacted",
            "date": date(2018, 6, 20),
        }
        timeline = make_timeline_data(meta, "document")
        self.assertIsNone(timeline)

    def test_multiple_versions_viewing_dated(self):
        meta = {
            "shortType": "ukpga",
            "year": 2023,
            "number": 1,
            "versions": ["enacted", "2022-01-01", "2024-01-01"],
            "version": "2024-01-01",
            "date": date(2018, 6, 20),
        }
        timeline = make_timeline_data(meta, "document")
        self.assertIsNotNone(timeline)
        labels = [e["label"] for e in timeline["entries"]]
        self.assertNotIn("enacted", labels)
        self.assertEqual(labels, ["2022-01-01"])
        self.assertEqual(timeline["current"]["label"], "2024-01-01")

    def test_two_versions_enacted_plus_date(self):
        meta = {
            "shortType": "ukpga",
            "year": 2023,
            "number": 1,
            "versions": ["enacted", "2024-01-01"],
            "version": "2024-01-01",
            "date": date(2018, 6, 20),
        }
        timeline = make_timeline_data(meta, "document")
        self.assertIsNotNone(timeline)
        self.assertEqual(timeline["entries"], [])
        self.assertEqual(timeline["current"]["label"], "2024-01-01")
        self.assertTrue(timeline["single_version"])


class TimelineTemplateTests(SimpleTestCase):

    def test_single_version_timeline_renders_disabled_summary(self):
        meta = {
            "shortType": "ukpga",
            "year": 2023,
            "number": 1,
            "versions": ["enacted"],
            "version": "enacted",
            "date": date(2018, 6, 20),
        }

        timeline = make_timeline_data(meta, "document")
        html = render_to_string(
            "new_theme/document/timeline.html", {"timeline": timeline}
        )

        self.assertTrue(timeline["single_version"])
        self.assertIn("<summary disabled>", html)
        self.assertIn("<ol>", html)

    def test_template_preserves_point_in_time_marker_for_historical_view(self):
        meta = {
            "shortType": "ukpga",
            "year": 2023,
            "number": 1,
            "versions": ["enacted", "2022-01-01", "2024-01-01"],
            "version": "2022-01-01",
            "date": date(2018, 6, 20),
            "pointInTime": date(2023, 6, 1),
        }

        timeline = make_timeline_data(meta, "document")
        html = render_to_string(
            "new_theme/document/timeline.html", {"timeline": timeline}
        )

        self.assertIn('class="point-in-time"', html)
        self.assertIn("01 June 2023", html)

    def test_template_uses_original_label_for_sole_version(self):
        meta = {
            "shortType": "ukpga",
            "year": 2023,
            "number": 1,
            "versions": ["made"],
            "version": "made",
            "date": date(2018, 6, 20),
        }

        timeline = make_timeline_data(meta, "document")
        html = render_to_string(
            "new_theme/document/timeline.html", {"timeline": timeline}
        )

        self.assertIn("as made on", html)
