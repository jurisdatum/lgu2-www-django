# ADR: Timeline changes — enacted/made visibility and data model

**Date:** 2026-05-18
**Status:** Proposed
**Deciders:** Jim Mangiafico (implementing); change requested by UX/editorial team

## Context

The timeline component shows all available versions of a legislation document, ordered chronologically. Currently, the enacted/made version always appears on the timeline as "the original version" when it exists, regardless of how many other versions are present. The `TimelineData` structure reflects this with a dedicated `original` field, separate from `historical` and `current`.

The UX team wants to experiment with removing the enacted/made version from the timeline when other (dated) versions exist. The motivation is that the enacted/made version is qualitatively different from dated versions — it represents the state of the document upon enactment, which may never have been in force and may never have been the law — and its presence on the timeline alongside amendment dates is potentially confusing to users.

At the same time, the UX team wants every document's "most recent version" view to show a timeline. For documents that have only one version (the enacted/made version), that version *is* the most recent version, so it must appear on the timeline to satisfy this requirement.

These two goals create a specific interaction when a user navigates to the enacted/made version of a document that has other versions: the enacted/made version would not be on the timeline, which means the version being viewed would not appear on the timeline. Showing a timeline that does not include the version being viewed would be disorienting, so the timeline must be hidden entirely in that case.

Additionally, the UX team has decided that the timeline should not appear on Table of Contents (ToC) pages at all. Currently, the ToC view calls `make_timeline_data()` and passes the result to the template, so ToC pages show the same timeline as document and fragment pages. The rationale for removing it is that the ToC is a navigation surface, not a reading surface — version context belongs on the document and fragment views where the user is actually reading legislation content.

### Current behaviour

- `_make_timeline_data()` always includes the original (enacted/made) version as `timeline['original']`, a dedicated field separate from `historical` and `current`.
- The timeline section always renders when timeline data is present.
- `single_version` disables the expand/collapse control but still shows the timeline summary.
- The template has separate rendering blocks for `original`, `historical` entries, and `current`.
- The ToC view generates and renders timeline data identically to document and fragment views.

### Desired behaviour

| Scenario | Timeline visible? | Enacted/made on it? |
|---|---|---|
| Enacted/made is the **only** version | Yes (non-expandable) | Yes (as `current`) |
| Multiple versions exist, viewing enacted/made | **No** (section hidden) | N/A |
| Multiple versions exist, viewing any other version | Yes | **No** |

**Invariant:** the user never sees a timeline that omits the version they are currently viewing.

## Decision

Three changes — two behavioural and one structural:

### 1. Enacted/made visibility rules

Modify `_make_timeline_data()` in `lgu2/util/timeline.py` to implement the new visibility rules. The function's return type changes from `TimelineData` to `Optional[TimelineData]`, returning `None` when the timeline should be hidden.

- **Multiple versions exist and the user is viewing the enacted/made version:** return `None`. The caller passes `None` to the template context, and the existing `{% if timeline %}` guard in `document.html` suppresses the entire timeline section.

- **Multiple versions exist and the user is not viewing the enacted/made version:** exclude the enacted/made version from the timeline entirely. The timeline shows only dated and prospective versions.

- **Only one version exists (the enacted/made version):** the enacted/made version appears on the timeline as `current`. The timeline renders with a single non-expandable entry.

### 2. Remove the timeline from ToC pages

The ToC view stops generating timeline data. The `make_timeline_data()` call in `views/toc.py` is removed, and no `timeline` key is passed to the template context. The timeline include in `toc.html` is currently unconditional (unlike `document.html`, which has an `{% if timeline %}` guard), so the include must also be removed from the ToC template.

The `make_timeline_data` function's `target` parameter currently accepts `'toc'` to generate ToC-specific links. With no ToC caller, `'toc'` is no longer a supported value and is removed from the parameter's documented options. The URL-building logic itself is unchanged — it still constructs route names dynamically from the `target` string — but no caller passes `'toc'` any more.

### 3. Remove the `original` field from `TimelineData`

The dedicated `original` field on `TimelineData` was justified when the enacted/made version always appeared on the timeline alongside dated versions and needed distinct structural treatment. Under the new rules, this is no longer the case: the enacted/made version either *is* the current entry (when it's the sole version) or it is absent from the timeline entirely. It never coexists with other entries.

The `TimelineData` structure changes from:

```python
class TimelineData(TypedDict):
    original: Optional[TimelineEntry]
    current: Optional[TimelineEntry]
    historical: List[TimelineEntry]
    viewing: TimelineEntry
    pointInTime: Optional[date]
    single_version: bool
```

to:

```python
class TimelineData(TypedDict):
    entries: List[TimelineEntry]   # all versions before the latest, in chronological order
    current: TimelineEntry         # the latest version — always visible, even when collapsed
    viewing: TimelineEntry         # whichever entry corresponds to the version being viewed
    pointInTime: Optional[date]
    single_version: bool
```

The three-bucket model (`original` / `historical` / `current`) collapses to two: `entries` (everything before the latest) and `current` (the latest, which gets special presentation treatment — it remains visible when the timeline is collapsed).

When the enacted/made version is the sole version, it becomes `current`. Its `label` field (`'enacted'`, `'made'`, `'created'`, `'adopted'`) tells the template how to render it — "as enacted on [date]" rather than "from [date]". Since Django templates cannot access Python sets like `_first` in `version.py`, the template uses literal label checks (e.g. `{% if current.label == 'enacted' or current.label == 'made' or current.label == 'created' or current.label == 'adopted' %}`) to distinguish enacted/made entries from dated ones. All four labels must be covered.

### Why restructure the data model alongside the visibility change

The visibility change alone could be implemented by nulling out the existing `original` field when other versions are present. But the `original` field would then be non-`None` only when it's the sole version — in which case it's also the current/latest. A field that is either `None` or redundant with `current` is dead weight in the data model and a source of confusion for future work on the timeline.

Removing it now, while the enacted/made semantics are actively being reworked, is the natural time to clean up the structure. It also simplifies the template from three distinct rendering blocks to a loop over `entries` plus a dedicated block for `current`.

### Why handle visibility in `_make_timeline_data` rather than in views or templates

- The timeline module already owns the decision of which entries appear and how they are structured. Adding visibility rules here keeps timeline logic in one place.
- Views already pass `timeline` through to the template without introspection; they do not need to learn about enacted/made semantics.
- The template already handles `None` timeline data via `{% if timeline %}`.

## Details

### Files changed

**`lgu2/util/timeline.py`**
- Replace the `TimelineData` TypedDict: remove `original` and `historical`; replace optional `current` with required `current`; add `entries` as described above.
- `make_timeline_data` return type: `TimelineData` → `Optional[TimelineData]`.
- `_make_timeline_data` return type: same change.
- Rewrite the entry-extraction logic:
  1. Pop and hold aside the enacted/made label from the front of the versions list if present (so it doesn't become an `entries` item or `current`).
  2. If no versions remain (the enacted/made label was the only version): the held-aside version becomes `current`.
  3. If other versions remain: the last becomes `current`, the rest become `entries`. The held-aside enacted/made version is discarded.
  4. If the user is viewing the enacted/made version and other versions exist: return `None`.

**`lgu2/templates/new_theme/document/timeline.html`**
- Replace the three separate rendering blocks (`original`, `historical` loop, `current`) with a single loop over `entries` plus a dedicated block for `current`.
- The summary section adapts: when `current.label` is in the enacted/made set, render "the original version" / "as enacted on"; otherwise render "the current version" / "from" as before.

**`lgu2/views/toc.py`**
- Remove the `make_timeline_data` call and the `timeline` import.
- No `timeline` key in the template context.

**`lgu2/templates/new_theme/document/toc.html`**
- Remove the `{% include "new_theme/document/timeline.html" %}` line (currently unconditional at line 33).

**`lgu2/tests/util/test_timeline.py`**
- Add test: single enacted version → timeline returned, `current.label == 'enacted'`, `entries` is empty, `single_version` is `True`.
- Add test: multiple versions, viewing enacted → `None` returned.
- Add test: multiple versions, viewing dated version → timeline returned, enacted excluded, `entries` contains intermediate versions.
- Add test: exactly two versions (enacted + one date) → timeline returned, `entries` is empty, `current` is the date, `single_version` is `True`.
- Remove `TocTimelineTests` class (ToC no longer uses the timeline).
- Update existing tests to use the new `entries`/`current` structure instead of `original`/`historical`/`current`.

### Edge cases

**Document with exactly two versions (enacted + one date):** the enacted version is excluded, leaving just the dated version as `current` with an empty `entries` list. `single_version` is `True`, so the expand control is disabled. This satisfies the "most recent version always has a timeline" requirement.

**Prospective-only documents:** a document with versions `['enacted', 'prospective']` viewing `prospective` will show a timeline with just the prospective entry as `current`. The enacted version is excluded. This follows the same rule as any other multi-version case.

**Fragment views:** the same `make_timeline_data` function serves both document and fragment views. The enacted/made visibility rules apply uniformly — the timeline semantics do not vary between these two view types.

**Template rendering of enacted-as-current:** when `current.label` is `'enacted'`, `'made'`, `'created'`, or `'adopted'`, the template renders "as [label] on [date]" instead of "from [date]". This reuses the label-detection logic already present in the template's original block, now applied to `current` via literal checks against all four labels.

**Semantic shift of `single_version`:** this field currently means "one version exists in total." Under the new rules, its meaning shifts to "one version is visible on the timeline." For example, a document with versions `['enacted', '2024-01-01']` has two versions, but the timeline shows only `2024-01-01`, so `single_version` is `True`. This is the correct semantics for the template — it controls whether the expand/collapse control is disabled — but the name now describes visible entry count rather than total version count. A rename (e.g. `single_entry`) could clarify this, but is deferred to avoid unnecessary churn.

### What this ADR does not cover

- **How users navigate to the enacted/made version** when it is not on the timeline. The UX team will provide a separate mechanism (likely a link elsewhere on the page). That work is independent of this change.
- **Point-in-time interaction.** The `pointInTime` field on the timeline is unaffected. When viewing a dated version with a point-in-time marker, the timeline renders as before, just without the enacted/made entry.

## Consequences

- The timeline data model becomes simpler: two buckets (`entries` + `current`) instead of three (`original` + `historical` + `current`).
- The template simplifies from three distinct rendering blocks to a loop plus one block.
- The enacted/made version page for multi-version documents loses its timeline. Users must reach the enacted/made version via whatever alternative navigation the UX team provides.
- Every "most recent version" view on document and fragment pages retains a timeline, satisfying the UX requirement.
- ToC pages no longer show a timeline. The `'toc'` target path through `make_timeline_data` is removed.
- Future timeline changes (additional entry types, different ordering, new presentation rules) work against a cleaner two-bucket model.

## Alternatives considered

- **Keep the `original` field, set it to `None` when other versions exist.** Less code churn, but leaves a field in the data model that is either `None` or redundant with `current`. The structural mismatch would need cleaning up eventually; doing it now while the semantics are changing is cheaper.
- **Hide timeline in the template via a CSS class or conditional.** Would work but splits timeline visibility logic between Python (which entries to show) and templates (whether to show the section). Keeping it in one place is simpler.
- **Add a `visible` boolean to `TimelineData` instead of returning `None`.** Marginally more explicit, but introduces a field that every template consumer must check, when `None` already conveys "no timeline" naturally.
- **Handle in views rather than in `_make_timeline_data`.** Would require each view (document, fragment, ToC) to independently implement the same enacted/made visibility check. Violates the existing pattern where timeline logic is centralised.
- **Add a boolean `enacted` field to `TimelineEntry`.** Would allow templates to style enacted/made entries differently. Deferred: the label already carries this information (via the `_first` set in `version.py`), and no design currently calls for distinct styling. Easy to add later if needed.
