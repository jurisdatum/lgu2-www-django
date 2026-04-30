"""Status messaging for legislation pages.

See docs/adr/2026-04-27-status-messaging-architecture.md and
docs/status_messages.md (the authoritative prose). This module and the
templates under lgu2/templates/status/ are the only places that should
construct or introspect a Status — its shape is unstable by design and
is derived from the templates that consume it.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple

from django.urls import reverse
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from .util.dated_version import is_most_recent_version
from .util.links import Link
from .util.version import is_first_version


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
    severity: str = ''  # '' | 'warning'
    disclosure: Optional[Disclosure] = None


@dataclass(frozen=True, slots=True)
class SidePanel:
    heading: str
    paragraphs: Tuple[str, ...] = ()
    button_expand_label: str = ''
    button_collapse_label: str = ''
    links: Tuple[Link, ...] = ()
    variant: str = 'up-to-date'  # 'up-to-date' | 'dated-version'
    severity: str = ''  # '' | 'warning'


@dataclass(frozen=True, slots=True)
class Status:
    messages: Tuple[Message, ...] = ()
    side_panel: Optional[SidePanel] = None


def _fragment_target_phrase(meta) -> str:
    """Return ``"{fragment_label} of {title}"`` for a fragment, else ``""``.

    Used by status copy that wants to address the surface the user is
    actually looking at — a section, schedule, etc. — rather than the
    whole document.
    """
    fragment_info = meta.get('fragmentInfo') or {}
    fragment_label = fragment_info.get('label') or ''
    title = meta.get('title', '')
    if not fragment_label:
        return ''
    return _("{fragment} of {title}").format(fragment=fragment_label, title=title)



def for_document(meta) -> Optional[Status]:
    # PDF-only documents are out of scope for this migration (catalog entry
    # `[ ] PDF only`). The legacy make_pdf_status_message path still renders
    # for them; returning None here prevents the two paths from doubling up.
    formats = meta.get('formats') or []
    if 'pdf' in formats and 'xml' not in formats:
        return None

    messages: List[Message] = []
    side_panel: Optional[SidePanel] = None

    if is_first_version(meta.get('version', '')):
        messages.append(Message(
            text=_("This is the original version (as it was originally made)."),
        ))

    title = meta.get('title', '')
    changes_link = Link(
        text=_("See all changes made to or by {title}").format(title=title),
        href=reverse(
            'changes-affected',
            args=[meta['shortType'], meta['year'], meta['number']],
        ),
    ) if meta.get('shortType') and meta.get('year') and meta.get('number') else None

    if is_most_recent_version(meta):
        outstanding = [e for e in (meta.get('unappliedEffects') or []) if e.get('outstanding')]
        if outstanding:
            expand_label = _("See what these changes are")
            collapse_label = _("Hide detail of these changes")
            messages.append(Message(
                heading=format_html(
                    _('There are outstanding changes not yet made by the '
                      'legislation.gov.uk editorial team to {title}.'),
                    title=title,
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
            ))
            side_panel = SidePanel(
                heading=_("Up to date status"),
                paragraphs=(
                    _("{title} is not up to date").format(title=title),
                    _("This legislation has been amended but we still need to update the website to reflect these changes."),
                ),
                button_expand_label=expand_label,
                button_collapse_label=collapse_label,
                links=(changes_link,) if changes_link else (),
                severity='warning',
            )
        else:
            side_panel = SidePanel(
                heading=_("Up to date status"),
                paragraphs=(
                    _("{title} is up to date with all known changes").format(title=title),
                ),
                links=(changes_link,) if changes_link else (),
            )

    if not messages and side_panel is None:
        return None
    return Status(messages=tuple(messages), side_panel=side_panel)


def for_fragment(meta) -> Optional[Status]:
    messages: List[Message] = []
    side_panel: Optional[SidePanel] = None

    if is_first_version(meta.get('version', '')):
        messages.append(Message(
            text=_("This is the original version (as it was originally made)."),
        ))

    title = meta.get('title', '')
    target = _fragment_target_phrase(meta) or title
    changes_link = Link(
        text=_("See all changes made to or by {title}").format(title=title),
        href=reverse(
            'changes-affected',
            args=[meta['shortType'], meta['year'], meta['number']],
        ),
    ) if meta.get('shortType') and meta.get('year') and meta.get('number') else None

    if is_most_recent_version(meta):
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
            expand_label = _("See what these changes are")
            collapse_label = _("Hide detail of these changes")
            messages.append(Message(
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
            ))
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
        else:
            side_panel = SidePanel(
                heading=_("Up to date status"),
                paragraphs=(
                    _("{target} is up to date with all known changes").format(target=target),
                ),
                links=(changes_link,) if changes_link else (),
            )

    if not messages and side_panel is None:
        return None
    return Status(messages=tuple(messages), side_panel=side_panel)



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
