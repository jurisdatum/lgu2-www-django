"""Dated-version panel for legislation pages.

The panel shown when a user is viewing a non-current (historical) version.
This is a viewing-context notice — "you are looking at a snapshot; here is
how to reach the current version" — not a status message.  It is rendered
by its own template and is not part of the status bounded context.
"""

from dataclasses import dataclass
from datetime import date as _Date
from typing import List, Optional, Tuple

from django.utils.formats import date_format
from django.utils.translation import gettext as _

from .links import Link, make_changes_affected_link, make_document_link


@dataclass(frozen=True, slots=True)
class VersionPanel:
    heading: str
    paragraphs: Tuple[str, ...] = ()
    links: Tuple[Link, ...] = ()


def is_most_recent_version(meta) -> bool:
    versions = meta.get('versions') or []
    return bool(versions) and meta['version'] == versions[-1]


def target_phrase(meta) -> str:
    """Return ``"{fragment_label} of {title}"`` for a fragment, else just the title.

    The "addressed" surface — what status copy refers to as the thing the user
    is actually looking at (a section, schedule, etc.), rather than the whole
    document.
    """
    title = meta.get('title', '')
    fragment_label = (meta.get('fragmentInfo') or {}).get('label') or ''
    if not fragment_label:
        return title
    return _("{fragment} of {title}").format(fragment=fragment_label, title=title)


def _shown_milestone_date(meta) -> Optional[_Date]:
    version = meta.get('version', '')
    try:
        return _Date.fromisoformat(version)
    except (TypeError, ValueError):
        return meta.get('date')


def dated_version_panel(meta, lang: Optional[str] = None, most_recent_href: Optional[str] = None) -> VersionPanel:
    """Build the panel shown when viewing a non-most-recent version.

    ``lang`` is the route-slug language (``english``/``welsh``), not the
    API's ``en``/``cy`` code — see ``make_document_link``.

    ``most_recent_href`` overrides the default whole-document URL for the
    "See the most recent version" link. Pass the pre-built URL for the
    current surface (e.g. the fragment or contents URL) when the panel is
    not being built for a whole-document view.
    """
    target = target_phrase(meta)

    # The "see most recent version" link goes to the document/fragment/contents
    # route, which accepts regnal years; the "see all changes" link goes
    # to changes-affected, whose URL pattern is calendar-year-only. So
    # the two links use different year sources by design.
    if most_recent_href is None:
        most_recent_href = make_document_link(
            meta['shortType'],
            meta.get('regnalYear') or meta['year'],
            meta['number'],
            None,
            lang,
        )

    links: List[Link] = [Link(
        text=_("See the most recent version"),
        href=most_recent_href,
    )]
    changes_link = make_changes_affected_link(meta)
    if changes_link is not None:
        links.append(changes_link)

    paragraphs: List[str] = [
        _("This is not the most recent version of {target}.").format(target=target),
    ]
    shown_date = _shown_milestone_date(meta)
    if shown_date:
        paragraphs.append(
            _("This legislation has been changed since {date}.").format(
                date=date_format(shown_date, 'd F Y'),
            )
        )

    return VersionPanel(
        heading=_("Up to date status"),
        paragraphs=tuple(paragraphs),
        links=tuple(links),
    )
