from datetime import datetime
from django.utils import timezone


def build_status(meta, timeline):
    """
    Central status builder for document pages.
    Returns full status object used by templates.
    """

    message = _build_status_message(meta, timeline)

    status = {
        "message": message,
        "label": meta["title"],
        "up_to_date": meta["upToDate"],
        "effects": {
            "direct": _group_effects(meta["unappliedEffects"])
        },
        "direct_effects": meta["unappliedEffects"],
        "larger_effects": [],
        "has_future_effects": any(
            e.get("required") and not e.get("outstanding")
            for e in meta["unappliedEffects"]
        ),
    }

    return status


def _group_effects(unapplied_effects):
    return {
        "outstanding": [
            e for e in unapplied_effects if e.get("outstanding")
        ],
        "future": [
            e for e in unapplied_effects if e.get("required") and not e.get("outstanding")
        ],
        "unrequired": [
            e for e in unapplied_effects if not e.get("required")
        ],
    }


def _build_status_message(meta, timeline):
    """
    Builds correct message using timeline logic.
    """

    doc_title = meta["title"]

    custom_message = _timeline_message(meta, timeline)
    if custom_message:
        return custom_message

    today = datetime.now().strftime("%d %B %Y")

    if meta["upToDate"]:
        return f"{doc_title} is up to date with all changes known to be in force on or before {today}."
    else:
        return (
            f"There are outstanding changes not yet made by the legislation.gov.uk "
            f"editorial team to {doc_title}. Any changes already made appear in "
            f"the content and are referenced with annotations."
        )


def _timeline_message(meta, timeline):
    """
    Handles version-based messaging.
    """

    if not timeline:
        return None

    total_versions = (
        (1 if timeline["original"] else 0)
        + len(timeline["historical"])
        + (1 if timeline["current"] else 0)
    )

    viewing = timeline["viewing"]
    current = timeline["current"]

    # Only one version
    if total_versions == 1 and viewing:
        if viewing.get("date"):
            formatted_date = viewing["date"].strftime("%d %b %Y")
        else:
            formatted_date = (
                meta.get("pointInTime") or timezone.localdate()
            ).strftime("%d %b %Y")

        return f"This Act has not been updated since {formatted_date}."

    # Viewing older version
    if total_versions > 1 and current and viewing["label"] != current["label"]:
        viewing_date = viewing.get("date")
        if viewing_date:
            formatted_date = viewing_date.strftime("%d %b %Y")
            return f"This legislation may have been updated since {formatted_date}."

    return None