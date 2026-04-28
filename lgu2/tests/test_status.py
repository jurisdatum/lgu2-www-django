from pathlib import Path

from django.template import Context, Engine
from django.test import SimpleTestCase

from lgu2.status import StatusObject


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


class StatusObjectTests(SimpleTestCase):

    def test_constructs_with_label(self):
        s = StatusObject(label='Test Act 2024')
        self.assertEqual(s.label, 'Test Act 2024')

    def test_is_frozen(self):
        s = StatusObject(label='Test Act 2024')
        with self.assertRaises(Exception):
            s.label = 'Other'

    def test_rejects_unknown_field_at_construction(self):
        with self.assertRaises(TypeError):
            StatusObject(lable='oops')


class StatusTemplateHarnessTests(SimpleTestCase):

    def test_main_template_renders_label(self):
        out = _render('status/main.html', {'status': StatusObject(label='Test Act 2024')})
        self.assertIn('Test Act 2024', out)
        self.assertNotIn(INVALID, out)

    def test_side_panel_template_renders_label(self):
        out = _render('status/side_panel.html', {'status': StatusObject(label='Test Act 2024')})
        self.assertIn('Test Act 2024', out)
        self.assertNotIn(INVALID, out)

    def test_strict_harness_surfaces_missing_status(self):
        out = _render('status/main.html', {})
        self.assertIn(INVALID, out)
