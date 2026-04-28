"""Status messaging for legislation pages.

See docs/adr/2026-04-27-status-messaging-architecture.md. This module
and the templates under lgu2/templates/status/ are the only places that
should construct or introspect a StatusObject — its shape is unstable
by design.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StatusObject:
    label: str
