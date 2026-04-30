from pathlib import Path

from django.template import Context, Engine
from django.test import SimpleTestCase
from django.utils.safestring import mark_safe

from lgu2.status import (
    Disclosure,
    Link,
    Message,
    SidePanel,
    Status,
    for_document,
    for_fragment,
)
from lgu2.util.dated_version import dated_version_panel


# Sentinel for missing context variables under the strict status-template
# engine. Any rendered status output containing this string indicates a
# template/object contract bug — typically a renamed field or a typo.
INVALID = '!!!STATUS_MISSING!!!'

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / 'templates'


def _strict_engine() -> Engine:
    return Engine(
        dirs=[str(_TEMPLATES_DIR)],
        app_dirs=False,
        libraries={'i18n': 'django.templatetags.i18n'},
        string_if_invalid=INVALID,
    )


def _render(template_name: str, context: dict) -> str:
    template = _strict_engine().get_template(template_name)
    return template.render(Context(context))


class StatusDataclassTests(SimpleTestCase):

    def test_status_is_frozen(self):
        s = Status(messages=())
        with self.assertRaises(Exception):
            s.messages = ()

    def test_status_rejects_unknown_field(self):
        with self.assertRaises(TypeError):
            Status(mesages=())

    def test_message_is_frozen(self):
        m = Message(text='hello')
        with self.assertRaises(Exception):
            m.text = 'goodbye'

    def test_message_severity_defaults_to_empty(self):
        m = Message(text='hello')
        self.assertEqual(m.severity, '')

    def test_message_accepts_severity(self):
        m = Message(text='hello', severity='warning')
        self.assertEqual(m.severity, 'warning')


class ForDocumentTests(SimpleTestCase):

    def _meta(self, version, versions):
        return {
            'version': version,
            'versions': versions,
            'title': 'Test Act 2024',
            'shortType': 'ukpga',
            'year': '2024',
            'number': '1',
        }

    def test_returns_status_when_viewing_enacted_version(self):
        status = for_document(self._meta(version='enacted', versions=['enacted', '2024-06-01']))
        self.assertIsNotNone(status)
        self.assertEqual(len(status.messages), 1)

    def test_returns_status_when_single_version_with_label(self):
        status = for_document(self._meta(version='made', versions=['made']))
        self.assertIsNotNone(status)

    def test_returns_side_panel_when_dated_version_is_latest(self):
        status = for_document(self._meta(version='2024-06-01', versions=['enacted', '2024-06-01']))
        self.assertIsNotNone(status)
        self.assertEqual(status.messages, ())
        self.assertIsNotNone(status.side_panel)
        self.assertEqual(status.side_panel.severity, '')

    def test_returns_side_panel_when_versions_are_dates_only(self):
        status = for_document(self._meta(version='2024-06-01', versions=['2024-06-01']))
        self.assertIsNotNone(status)
        self.assertIsNotNone(status.side_panel)

    def test_returns_none_when_viewing_non_latest_historical_version(self):
        # for_document is narrowly about status messages; the dated-version
        # side panel is built separately by dated_version_panel().
        status = for_document(self._meta(
            version='2024-06-01',
            versions=['enacted', '2024-06-01', '2025-01-01'],
        ))
        self.assertIsNone(status)

    def test_returns_none_for_pdf_only_documents(self):
        # PDF-only docs are out of migration scope; the legacy
        # make_pdf_status_message path still renders for them, so for_document
        # must stay silent to avoid two status panels stacking.
        meta = self._meta(version='enacted', versions=['enacted'])
        meta['formats'] = ['pdf']
        self.assertIsNone(for_document(meta))

    def test_returns_status_for_documents_with_xml_and_pdf(self):
        meta = self._meta(version='enacted', versions=['enacted'])
        meta['formats'] = ['xml', 'pdf']
        self.assertIsNotNone(for_document(meta))

    def _meta_with_effects(self, version, versions, outstanding):
        meta = self._meta(version=version, versions=versions)
        meta['unappliedEffects'] = [{'outstanding': True}] if outstanding else []
        return meta

    def test_emits_red_message_when_most_recent_with_outstanding_effects(self):
        status = for_document(self._meta_with_effects(
            version='2024-06-01', versions=['enacted', '2024-06-01'], outstanding=True,
        ))
        self.assertIsNotNone(status)
        self.assertEqual(len(status.messages), 1)
        msg = status.messages[0]
        self.assertEqual(msg.severity, 'warning')
        self.assertIn('Test Act 2024', str(msg.heading))
        self.assertIn('outstanding changes', str(msg.heading))
        self.assertIn('appear in the content', str(msg.text))

    def test_no_red_message_when_no_outstanding_effects(self):
        status = for_document(self._meta_with_effects(
            version='2024-06-01', versions=['enacted', '2024-06-01'], outstanding=False,
        ))
        self.assertEqual(status.messages, ())
        # side panel still populated (up-to-date variant)
        self.assertIsNotNone(status.side_panel)
        self.assertEqual(status.side_panel.severity, '')

    def test_no_red_message_when_viewing_dated_non_current_version(self):
        # Outstanding effects exist, but we're not on the most recent version,
        # so the red message must not appear (and original doesn't apply either).
        status = for_document(self._meta_with_effects(
            version='2024-06-01',
            versions=['enacted', '2024-06-01', '2025-01-01'],
            outstanding=True,
        ))
        self.assertIsNone(status)

    def test_red_message_disclosure_carries_one_item_per_outstanding_effect(self):
        meta = self._meta(version='2024-06-01', versions=['enacted', '2024-06-01'])
        meta['unappliedEffects'] = [
            {
                'outstanding': True,
                'type': 'words substituted',
                'target': {'provisions': {'plain': 's. 1(2)(a)', 'rich': []}},
                'source': {
                    'id': 'uksi/2025/349',
                    'cite': 'S.I. 2025/349',
                    'provisions': {'plain': 's. 5(2)(a)', 'rich': [
                        {'type': 'link', 'text': 's. 5(2)(a)', 'href': 'uksi/2025/349/section/5/2/a'},
                    ]},
                },
            },
            {
                'outstanding': True,
                'type': 'inserted',
                'target': {'provisions': {'plain': 's. 86(9A)', 'rich': []}},
                'source': {
                    'id': 'uksi/2019/707',
                    'cite': 'S.I. 2019/707',
                    'provisions': {'plain': 'reg. 8(9)', 'rich': [
                        {'type': 'link', 'text': 'reg. 8(9)', 'href': 'uksi/2019/707/regulation/8/9'},
                    ]},
                },
            },
            {'outstanding': False, 'type': 'inserted'},  # filtered out
        ]
        status = for_document(meta)
        msg = status.messages[0]
        self.assertIsNotNone(msg.disclosure)
        self.assertEqual(len(msg.disclosure.items), 2)
        self.assertEqual(msg.disclosure.expand_label, 'See what these changes are')
        self.assertEqual(msg.disclosure.collapse_label, 'Hide detail of these changes')

    def test_effect_to_li_renders_target_verb_cite_and_provisions_link(self):
        from lgu2.status import _effect_to_li
        html = str(_effect_to_li({
            'type': 'words substituted',
            'target': {'provisions': {'plain': 's. 1(2)(a)'}},
            'source': {
                'id': 'uksi/2025/349',
                'cite': 'S.I. 2025/349',
                'provisions': {'rich': [
                    {'type': 'link', 'text': 's. 5(2)(a)', 'href': 'uksi/2025/349/section/5/2/a'},
                ]},
            },
        }))
        self.assertIn('<b>s. 1(2)(a)</b>', html)
        self.assertIn('words substituted by', html)
        self.assertIn('<a href="/uksi/2025/349">S.I. 2025/349</a>', html)
        self.assertIn('<a href="/uksi/2025/349/section/5/2/a">s. 5(2)(a)</a>', html)

    def test_effect_to_li_handles_missing_fields_without_crashing(self):
        from lgu2.status import _effect_to_li
        html = str(_effect_to_li({}))
        self.assertEqual(html, '<b></b>  by  ')  # degenerate but renders

    def test_effect_to_li_cite_without_id_renders_as_plain_text(self):
        from lgu2.status import _effect_to_li
        html = str(_effect_to_li({
            'type': 'inserted',
            'target': {'provisions': {'plain': 's. 1'}},
            'source': {'cite': 'S.I. 2024/54', 'provisions': {'rich': []}},
        }))
        self.assertIn('S.I. 2024/54', html)
        self.assertNotIn('<a href="/">', html)

    def test_side_panel_warning_when_most_recent_with_outstanding(self):
        status = for_document(self._meta_with_effects(
            version='2024-06-01', versions=['enacted', '2024-06-01'], outstanding=True,
        ))
        sp = status.side_panel
        self.assertEqual(sp.severity, 'warning')
        self.assertEqual(len(sp.paragraphs), 2)
        self.assertIn('Test Act 2024 is not up to date', sp.paragraphs[0])
        self.assertEqual(sp.button_expand_label, 'See what these changes are')
        self.assertEqual(sp.button_collapse_label, 'Hide detail of these changes')
        self.assertEqual(len(sp.links), 1)
        self.assertEqual(sp.links[0].href, '/changes/affected/ukpga/2024/1')
        self.assertIn('Test Act 2024', sp.links[0].text)

    def test_side_panel_up_to_date_when_most_recent_no_outstanding(self):
        status = for_document(self._meta_with_effects(
            version='2024-06-01', versions=['enacted', '2024-06-01'], outstanding=False,
        ))
        sp = status.side_panel
        self.assertEqual(sp.severity, '')
        self.assertEqual(len(sp.paragraphs), 1)
        self.assertIn('is up to date with all known changes', sp.paragraphs[0])
        self.assertEqual(sp.button_expand_label, '')  # no button on up-to-date
        self.assertEqual(len(sp.links), 1)
        self.assertEqual(sp.links[0].href, '/changes/affected/ukpga/2024/1')

    def test_both_messages_when_single_version_has_outstanding_effects(self):
        # A single-version document is both 'original' and 'most recent', so
        # both panels stack.
        status = for_document(self._meta_with_effects(
            version='enacted', versions=['enacted'], outstanding=True,
        ))
        self.assertIsNotNone(status)
        self.assertEqual(len(status.messages), 2)
        self.assertEqual(status.messages[0].severity, '')
        self.assertEqual(status.messages[1].severity, 'warning')


class ForFragmentTests(SimpleTestCase):

    def _meta(self, version, versions, *, fragment_label='Section 5', unapplied=None):
        return {
            'version': version,
            'versions': versions,
            'title': 'Test Act 2024',
            'shortType': 'ukpga',
            'year': '2024',
            'number': '1',
            'fragmentInfo': {'label': fragment_label, 'href': 'section/5'},
            'unappliedEffects': unapplied if unapplied is not None else {'fragment': [], 'ancestor': []},
        }

    def test_returns_status_when_viewing_enacted_fragment(self):
        status = for_fragment(self._meta(version='enacted', versions=['enacted', '2024-06-01']))
        self.assertIsNotNone(status)
        self.assertEqual(len(status.messages), 1)
        self.assertIn('original version', str(status.messages[0].text))

    def test_returns_none_when_viewing_non_latest_historical_version(self):
        status = for_fragment(self._meta(
            version='2024-06-01',
            versions=['enacted', '2024-06-01', '2025-01-01'],
        ))
        self.assertIsNone(status)

    def test_red_message_targets_fragment_of_title(self):
        status = for_fragment(self._meta(
            version='2024-06-01',
            versions=['enacted', '2024-06-01'],
            unapplied={'fragment': [{'outstanding': True}], 'ancestor': []},
        ))
        msg = status.messages[0]
        self.assertEqual(msg.severity, 'warning')
        self.assertIn('Section 5 of Test Act 2024', str(msg.heading))

    def test_side_panel_targets_fragment_of_title_when_up_to_date(self):
        status = for_fragment(self._meta(
            version='2024-06-01',
            versions=['enacted', '2024-06-01'],
        ))
        self.assertEqual(status.messages, ())
        self.assertIsNotNone(status.side_panel)
        self.assertIn('Section 5 of Test Act 2024', str(status.side_panel.paragraphs[0]))

    def test_outstanding_concatenates_direct_and_ancestor_in_order(self):
        # ADR C4: until grouped designs land, the disclosure is one flat
        # list with direct (fragment) effects first, then ancestor effects.
        direct = {
            'outstanding': True, 'type': 'inserted',
            'target': {'provisions': {'plain': 's. 5(2)', 'rich': []}},
            'source': {'cite': 'D1'},
        }
        ancestor = {
            'outstanding': True, 'type': 'inserted',
            'target': {'provisions': {'plain': 'Pt. 2', 'rich': []}},
            'source': {'cite': 'A1'},
        }
        non_outstanding_direct = {'outstanding': False, 'type': 'inserted'}
        status = for_fragment(self._meta(
            version='2024-06-01',
            versions=['enacted', '2024-06-01'],
            unapplied={'fragment': [direct, non_outstanding_direct], 'ancestor': [ancestor]},
        ))
        msg = status.messages[0]
        self.assertEqual(len(msg.disclosure.items), 2)
        # direct comes first
        self.assertIn('s. 5(2)', str(msg.disclosure.items[0]))
        self.assertIn('Pt. 2', str(msg.disclosure.items[1]))

    def test_handles_empty_unapplied_effects_dict(self):
        status = for_fragment(self._meta(
            version='2024-06-01',
            versions=['enacted', '2024-06-01'],
            unapplied={'fragment': [], 'ancestor': []},
        ))
        # most-recent + no outstanding → up-to-date side panel only
        self.assertEqual(status.messages, ())
        self.assertIsNotNone(status.side_panel)
        self.assertEqual(status.side_panel.severity, '')

    def test_falls_back_to_title_when_fragment_label_missing(self):
        meta = self._meta(version='2024-06-01', versions=['enacted', '2024-06-01'])
        meta['fragmentInfo'] = {}
        status = for_fragment(meta)
        self.assertIn('Test Act 2024', str(status.side_panel.paragraphs[0]))
        self.assertNotIn(' of Test Act 2024', str(status.side_panel.paragraphs[0]))


class DatedVersionPanelTests(SimpleTestCase):

    def _meta(self, **overrides):
        meta = {
            'title': 'Test Act 2024',
            'shortType': 'ukpga',
            'year': '2024',
            'number': '1',
            'version': '2024-06-01',
            'versions': ['enacted', '2024-06-01', '2025-01-01'],
        }
        meta.update(overrides)
        return meta

    def test_links_point_to_most_recent_and_changes(self):
        from datetime import date
        panel = dated_version_panel(self._meta(pointInTime=date(2024, 6, 1)))
        self.assertEqual(len(panel.links), 2)
        self.assertEqual(panel.links[0].href, '/ukpga/2024/1')
        self.assertIn('most recent version', panel.links[0].text)
        self.assertEqual(panel.links[1].href, '/changes/affected/ukpga/2024/1')

    def test_changed_since_uses_version_when_version_is_a_date(self):
        # The "changed since X" date is the milestone shown, not the
        # user-requested pointInTime. meta['version'] holds the milestone
        # date when the user is on a date-keyed view.
        from datetime import date
        panel = dated_version_panel(self._meta(
            version='2015-08-21',
            pointInTime=date(2020, 1, 1),  # ignored — user-requested date
        ))
        self.assertEqual(len(panel.paragraphs), 2)
        self.assertIn('21 August 2015', panel.paragraphs[1])

    def test_changed_since_uses_meta_date_for_labelled_versions(self):
        # When viewing a historical original-version page (e.g. /enacted)
        # of a later-amended document, meta['version'] is a label and the
        # enactment/made date lives in meta['date'].
        from datetime import date
        panel = dated_version_panel(self._meta(
            version='enacted',
            date=date(2010, 4, 1),
            versions=['enacted', '2015-08-21', '2020-01-01'],
        ))
        self.assertEqual(len(panel.paragraphs), 2)
        self.assertIn('1 April 2010', panel.paragraphs[1])

    def test_omits_changed_since_paragraph_when_no_milestone_date(self):
        panel = dated_version_panel(self._meta(version='enacted'))
        self.assertEqual(len(panel.paragraphs), 1)

    def test_welsh_route_lang_produces_welsh_most_recent_url(self):
        # Regression: meta['lang'] is 'en'/'cy' (API codes) but the URL
        # routes accept only 'english'/'welsh' (route slugs). The view must
        # pass the route slug; pulling from meta would NoReverseMatch.
        panel = dated_version_panel(self._meta(lang='cy'), lang='welsh')
        self.assertIn('/welsh', panel.links[0].href)

    def test_regnal_year_used_for_most_recent_link(self):
        # The document route accepts regnal years; we prefer regnalYear when
        # present so the canonical document URL is returned.
        panel = dated_version_panel(self._meta(
            shortType='ukpga', year='1948', regnalYear='Geo6/11-12', number='38',
        ))
        self.assertIn('/ukpga/Geo6/11-12/38', panel.links[0].href)
        # changes-affected uses calendar year (its URL pattern is calendar-only).
        self.assertEqual(panel.links[1].href, '/changes/affected/ukpga/1948/38')

    def test_most_recent_href_overrides_default_document_link(self):
        # The caller passes a pre-built URL so the panel can target any surface
        # (fragment, contents, etc.) rather than the whole-document route.
        meta = self._meta(fragmentInfo={'label': 'Section 5', 'href': 'section/5'})
        panel = dated_version_panel(meta, most_recent_href='/ukpga/2024/1/section/5')
        self.assertEqual(panel.links[0].href, '/ukpga/2024/1/section/5')
        self.assertIn('Section 5 of Test Act 2024', panel.paragraphs[0])


class StatusMainTemplateTests(SimpleTestCase):

    def test_renders_single_message_panel(self):
        out = _render('status/main.html', {
            'status': Status(messages=(Message(text='Hello world.'),)),
        })
        self.assertIn('Hello world.', out)
        self.assertIn('class="status-panel"', out)
        self.assertNotIn(INVALID, out)

    def test_renders_one_panel_per_message(self):
        out = _render('status/main.html', {
            'status': Status(messages=(Message(text='First.'), Message(text='Second.'))),
        })
        self.assertEqual(out.count('class="status-panel'), 2)
        self.assertIn('First.', out)
        self.assertIn('Second.', out)

    def test_renders_heading_when_present(self):
        out = _render('status/main.html', {
            'status': Status(messages=(Message(heading='Heads up.', text='Body.'),)),
        })
        self.assertIn('<h2>Heads up.</h2>', out)
        self.assertIn('<p>Body.</p>', out)

    def test_omits_heading_when_empty(self):
        out = _render('status/main.html', {
            'status': Status(messages=(Message(text='Just a body.'),)),
        })
        self.assertNotIn('<h2>', out)
        self.assertIn('<p>Just a body.</p>', out)

    def test_omits_text_when_empty(self):
        out = _render('status/main.html', {
            'status': Status(messages=(Message(heading='Heading only.'),)),
        })
        self.assertIn('<h2>Heading only.</h2>', out)
        self.assertNotIn('<p>', out)

    def test_warning_severity_maps_to_not_up_to_date_class(self):
        out = _render('status/main.html', {
            'status': Status(messages=(Message(text='Hello.', severity='warning'),)),
        })
        self.assertIn('class="status-panel not-up-to-date"', out)

    def test_omits_class_suffix_when_severity_is_empty(self):
        out = _render('status/main.html', {
            'status': Status(messages=(Message(text='Hello.'),)),
        })
        self.assertIn('class="status-panel"', out)
        self.assertNotIn('class="status-panel "', out)

    def test_renders_nothing_when_status_is_none(self):
        out = _render('status/main.html', {'status': None})
        self.assertNotIn('class="status-panel"', out)
        self.assertNotIn(INVALID, out)


class SidePanelTemplateTests(SimpleTestCase):

    def _render_with(self, side_panel):
        return _render('status/side_panel.html', {'panel': side_panel})

    def test_renders_nothing_when_panel_is_none(self):
        out = _render('status/side_panel.html', {'panel': None})
        self.assertNotIn('<h3>', out)
        self.assertNotIn(INVALID, out)

    def test_renders_up_to_date_variant(self):
        out = self._render_with(SidePanel(
            heading='Up to date status',
            paragraphs=('Foo Act is up to date with all known changes',),
            links=(Link(text='See all changes', href='/changes/affected/ukpga/2024/1'),),
        ))
        self.assertIn('class="up-to-date"', out)
        self.assertIn('<h3>Up to date status</h3>', out)
        self.assertIn('Foo Act is up to date', out)
        self.assertIn('href="/changes/affected/ukpga/2024/1"', out)
        self.assertNotIn('<button', out)

    def test_renders_not_up_to_date_variant(self):
        out = self._render_with(SidePanel(
            heading='Up to date status',
            paragraphs=('Foo Act is not up to date', 'It has been amended...'),
            button_expand_label='See what these changes are',
            button_collapse_label='Hide detail of these changes',
            links=(Link(text='See all changes', href='/changes/affected/ukpga/2024/1'),),
            severity='warning',
        ))
        self.assertIn('class="up-to-date not-up-to-date"', out)
        self.assertIn('<button', out)
        self.assertIn('data-expand-label="See what these changes are"', out)
        self.assertIn('data-collapse-label="Hide detail of these changes"', out)
        self.assertEqual(out.count('<p>'), 2)

    def test_renders_dated_version_variant(self):
        out = self._render_with(SidePanel(
            heading='Up to date status',
            paragraphs=(
                'This is not the most recent version of Foo Act.',
                'This legislation has been changed since 21 August 2015.',
            ),
            links=(
                Link(text='See the most recent version', href='/ukpga/2015/1'),
                Link(text='See all changes', href='/changes/affected/ukpga/2015/1'),
            ),
            variant='dated-version',
        ))
        self.assertIn('class="dated-version"', out)
        self.assertNotIn('not-up-to-date', out)
        self.assertNotIn('<button', out)
        self.assertIn('href="/ukpga/2015/1"', out)
        self.assertIn('href="/changes/affected/ukpga/2015/1"', out)
        self.assertEqual(out.count('<a '), 2)


class DisclosureRenderingTests(SimpleTestCase):

    def _disclosure(self, **overrides):
        defaults = dict(
            items=(
                mark_safe('<span>s. 1 </span>coming into force'),
                mark_safe('<span>s. 2 </span>repealed'),
            ),
            collapsed_initially=True,
            expand_label='See what these changes are',
            collapse_label='Hide detail of these changes',
        )
        defaults.update(overrides)
        return Disclosure(**defaults)

    def _render_with(self, disclosure):
        return _render('status/main.html', {
            'status': Status(messages=(
                Message(heading='H', text='T', disclosure=disclosure),
            )),
        })

    def test_renders_details_when_disclosure_present(self):
        out = self._render_with(self._disclosure())
        self.assertIn('<details', out)
        self.assertIn('<summary', out)
        self.assertIn('<ul>', out)

    def test_details_carries_id_referenced_by_side_panel_button(self):
        # The side-panel button declares aria-controls="statusPanelDetail";
        # the <details> in the main pane must carry that id so screen
        # readers (and the JS that toggles them in tandem) can pair them.
        out = self._render_with(self._disclosure())
        self.assertIn('id="statusPanelDetail"', out)

    def test_omits_details_when_no_disclosure(self):
        out = _render('status/main.html', {
            'status': Status(messages=(Message(heading='H', text='T'),)),
        })
        self.assertNotIn('<details', out)

    def test_renders_items_as_list_with_html_unescaped(self):
        out = self._render_with(self._disclosure())
        self.assertIn('<li><span>s. 1 </span>coming into force</li>', out)
        self.assertIn('<li><span>s. 2 </span>repealed</li>', out)

    def test_renders_data_attributes_for_labels(self):
        out = self._render_with(self._disclosure())
        self.assertIn('data-expand-label="See what these changes are"', out)
        self.assertIn('data-collapse-label="Hide detail of these changes"', out)

    def test_summary_text_uses_expand_label_when_collapsed_initially(self):
        out = self._render_with(self._disclosure(collapsed_initially=True))
        self.assertIn('>See what these changes are</summary>', out)
        self.assertNotIn(' open>', out)

    def test_summary_text_uses_collapse_label_when_open_initially(self):
        out = self._render_with(self._disclosure(collapsed_initially=False))
        self.assertIn('>Hide detail of these changes</summary>', out)
        self.assertIn(' open>', out)
