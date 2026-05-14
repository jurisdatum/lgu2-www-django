"""Status messaging for legislation pages.

See docs/adr/2026-04-27-status-messaging-architecture.md and
docs/status_messages.md (the authoritative prose). This module and the
templates under lgu2/templates/status/ are the only places that should
construct or introspect a Status — its shape is unstable by design and
is derived from the templates that consume it.
"""

from dataclasses import dataclass
from typing import List, Literal, Optional, Tuple

from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from .util.dated_version import is_most_recent_version, target_phrase
from .util.links import Link, make_changes_affected_link
from .util.version import is_first_version


Severity = Literal['', 'warning']
PanelVariant = Literal['up-to-date', 'dated-version']


@dataclass(frozen=True, slots=True)
class Disclosure:
    items: Tuple[str, ...] = ()
    collapsed_initially: bool = True
    expand_label: str = ''
    collapse_label: str = ''


@dataclass(frozen=True, slots=True)
class Message:
    heading: str = ''
    text: str = ''
    severity: Severity = ''
    disclosure: Optional[Disclosure] = None


@dataclass(frozen=True, slots=True)
class SidePanel:
    heading: str
    paragraphs: Tuple[str, ...] = ()
    button_expand_label: str = ''
    button_collapse_label: str = ''
    links: Tuple[Link, ...] = ()
    variant: PanelVariant = 'up-to-date'
    severity: Severity = ''


@dataclass(frozen=True, slots=True)
class Status:
    messages: Tuple[Message, ...] = ()
    side_panel: Optional[SidePanel] = None


def _outstanding_block(target: str, outstanding, changes_link: Optional[Link]) -> Tuple[Message, SidePanel]:
    expand_label = _("See what these changes are")
    collapse_label = _("Hide detail of these changes")
    message = Message(
        heading=format_html(
            _('There are outstanding changes not yet made by the '
              'legislation.gov.uk editorial team to {target}.'),
            target=target,
        ),
        text=_(
            'Any changes that have already been made by the team appear '
            'in the content and are referenced with annotations.'
        ),
        severity='warning',
        disclosure=Disclosure(
            items=tuple(_effect_to_li(e) for e in outstanding),
            collapsed_initially=True,
            expand_label=expand_label,
            collapse_label=collapse_label,
        ),
    )
    side_panel = SidePanel(
        heading=_("Up to date status"),
        paragraphs=(
            _("{target} is not up to date").format(target=target),
            _("This legislation has been amended but we still need to update the website to reflect these changes."),
        ),
        button_expand_label=expand_label,
        button_collapse_label=collapse_label,
        links=(changes_link,) if changes_link else (),
        severity='warning',
    )
    return message, side_panel


def _up_to_date_panel(target: str, changes_link: Optional[Link]) -> SidePanel:
    return SidePanel(
        heading=_("Up to date status"),
        paragraphs=(
            _("{target} is up to date with all known changes").format(target=target),
        ),
        links=(changes_link,) if changes_link else (),
    )


def _original_version_message() -> Message:
    return Message(text=_("This is the original version (as it was originally made)."))


def _finalize(messages: List[Message], side_panel: Optional[SidePanel]) -> Optional[Status]:
    if not messages and side_panel is None:
        return None
    return Status(messages=tuple(messages), side_panel=side_panel)


def for_document(meta) -> Optional[Status]:
    # PDF-only documents fall through to the legacy make_pdf_status_message
    # path; returning None here prevents the two paths from doubling up.
    formats = meta.get('formats') or []
    if 'pdf' in formats and 'xml' not in formats:
        return None

    messages: List[Message] = []
    side_panel: Optional[SidePanel] = None

    if is_first_version(meta.get('version', '')):
        messages.append(_original_version_message())

    if is_most_recent_version(meta):
        title = meta.get('title', '')
        changes_link = make_changes_affected_link(meta)
        outstanding = [e for e in (meta.get('unappliedEffects') or []) if e.get('outstanding')]
        if outstanding:
            message, side_panel = _outstanding_block(title, outstanding, changes_link)
            messages.append(message)
        else:
            side_panel = _up_to_date_panel(title, changes_link)

    return _finalize(messages, side_panel)


def for_fragment(meta) -> Optional[Status]:
    messages: List[Message] = []
    side_panel: Optional[SidePanel] = None

    if is_first_version(meta.get('version', '')):
        messages.append(_original_version_message())

    if is_most_recent_version(meta):
        target = target_phrase(meta)
        changes_link = make_changes_affected_link(meta)
        # Per ADR C4: the API splits fragment outstanding effects into
        # ``fragment`` (direct + descendants) and ``ancestor`` (parents
        # propagating down). Until grouped designs and CSS arrive we
        # concatenate them into one flat list rather than drop one group
        # (as the old new-theme template did) or invent UI ahead of design.
        unapplied = meta.get('unappliedEffects') or {}
        outstanding = [
            e for e in (unapplied.get('fragment') or []) if e.get('outstanding')
        ] + [
            e for e in (unapplied.get('ancestor') or []) if e.get('outstanding')
        ]
        if outstanding:
            message, side_panel = _outstanding_block(target, outstanding, changes_link)
            messages.append(message)
        else:
            side_panel = _up_to_date_panel(target, changes_link)

    return _finalize(messages, side_panel)


def _render_rich(nodes):
    parts = []
    for node in nodes or []:
        if node.get('type') == 'link':
            parts.append(format_html(
                '<a href="/{}">{}</a>',
                node.get('href', ''),
                node.get('text', ''),
            ))
        else:
            parts.append(escape(node.get('text', '')))
    return mark_safe(''.join(parts))


def _effect_to_li(effect):
    target_plain = (effect.get('target') or {}).get('provisions', {}).get('plain', '')
    verb_phrase = effect.get('type', '')
    source = effect.get('source') or {}
    cite = source.get('cite', '')
    source_id = source.get('id', '')
    cite_html = (
        format_html('<a href="/{}">{}</a>', source_id, cite)
        if cite and source_id
        else escape(cite)
    )
    source_rich = _render_rich((source.get('provisions') or {}).get('rich', []))
    return format_html(
        '<b>{target}</b> {verb} by {cite_html} {source_rich}',
        target=target_plain,
        verb=_(verb_phrase),
        cite_html=cite_html,
        source_rich=source_rich,
    )
