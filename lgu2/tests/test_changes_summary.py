from django.test import SimpleTestCase

from lgu2.views.changes.summary import build_changes_summary


TYPES = {
    'ukpga': 'UK Public General Acts',
    'uksi': 'UK Statutory Instruments',
}


def _empty_form_values(**overrides):
    base = {
        f'{side}_{attr}': ''
        for side in ['affected', 'affecting']
        for attr in ['type', 'year', 'start_year', 'end_year', 'number', 'title']
    }
    base.update(overrides)
    return base


class DetailSummaryTests(SimpleTestCase):

    def _detail_text(self, form_values):
        summary = build_changes_summary(form_values, TYPES)
        return summary.detail_intro + ''.join(c.text for c in summary.detail_clauses) + '.'

    def test_minimal_query(self):
        text = self._detail_text(_empty_form_values())
        self.assertEqual(text, 'for All changes to any legislation, made by any legislation.')

    def test_type_and_year(self):
        text = self._detail_text(_empty_form_values(
            affected_type='ukpga', affected_year='2024',
        ))
        self.assertEqual(text,
                         'for All changes to UK Public General Acts'
                         ', enacted or made in 2024'
                         ', made by any legislation.')

    def test_year_range(self):
        text = self._detail_text(_empty_form_values(
            affected_type='uksi',
            affected_start_year='1996', affected_end_year='1998',
        ))
        self.assertEqual(text,
                         'for All changes to UK Statutory Instruments'
                         ', enacted or made between 1996 and 1998'
                         ', made by any legislation.')

    def test_same_start_and_end_year(self):
        text = self._detail_text(_empty_form_values(
            affected_type='uksi',
            affected_start_year='2020', affected_end_year='2020',
        ))
        self.assertIn('in 2020', text)
        self.assertNotIn('between', text)

    def test_title_filter(self):
        text = self._detail_text(_empty_form_values(
            affected_type='uksi', affected_title='Housing Act',
        ))
        self.assertIn('with the title \u201cHousing Act\u201d', text)

    def test_number_filter(self):
        text = self._detail_text(_empty_form_values(
            affected_type='uksi', affected_number='123',
        ))
        self.assertIn('with the number \u201c123\u201d', text)

    def test_applied_uses_of_connector(self):
        text = self._detail_text(_empty_form_values(applied='applied'))
        self.assertIn('Changes that have been applied to the text of', text)
        self.assertNotIn(' to any legislation', text)

    def test_unapplied_uses_of_connector(self):
        text = self._detail_text(_empty_form_values(applied='unapplied'))
        self.assertIn('Changes not yet applied to the text of', text)

    def test_all_changes_uses_to_connector(self):
        text = self._detail_text(_empty_form_values())
        self.assertIn('All changes to', text)

    def test_absent_fields_omitted(self):
        text = self._detail_text(_empty_form_values())
        self.assertNotIn('with the title', text)
        self.assertNotIn('enacted or made', text)
        self.assertNotIn('with the number', text)

    def test_affecting_side(self):
        text = self._detail_text(_empty_form_values(
            affecting_type='ukpga', affecting_year='2020',
        ))
        self.assertIn(', made by UK Public General Acts, enacted or made in 2020', text)


class FormInitialTests(SimpleTestCase):

    def test_form_initial_has_resolved_labels(self):
        form_values = _empty_form_values(affected_type='ukpga', applied='applied')
        summary = build_changes_summary(form_values, TYPES)
        self.assertEqual(summary.form_initial['affectedType'], 'UK Public General Acts')
        self.assertIn('of', summary.form_initial['showChanges'])

    def test_form_initial_has_year_text(self):
        form_values = _empty_form_values(affected_year='2024')
        summary = build_changes_summary(form_values, TYPES)
        self.assertEqual(summary.form_initial['affectedYear'], 'in 2024')

    def test_form_initial_keys_match_js_ids(self):
        summary = build_changes_summary(_empty_form_values(), TYPES)
        expected_keys = {
            'showChanges', 'affectedType', 'affectedTitle', 'affectedYear',
            'affectedNumber', 'affectingType', 'affectingTitle', 'affectingYear',
            'affectingNumber',
        }
        self.assertEqual(set(summary.form_initial.keys()), expected_keys)
