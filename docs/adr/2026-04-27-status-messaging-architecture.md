# ADR: Status messaging architecture

**Date:** 2026-04-27
**Status:** Proposed
**Deciders:** Jim Mangiafico

## Context

A "status message" is the block of information shown above the main text of a legislation document, telling the reader what they are looking at: whether the displayed version is current, whether amendments are outstanding, whether changes are pending in the future, whether they are looking at a historical or original-only version, and so on. It currently lives in scattered places:

- `lgu2/messages/status.py` — historically string-returning functions for document and fragment views; PR 62 starts turning this into a richer status dict
- `lgu2/views/helper/status.py` — a richer `make_status_data()` returning a dict, plus `make_pdf_status_message()` and a four-way `group_effects()` taxonomy
- `lgu2/templates/new_theme/document/status_panel.html`, `up_to_date.html`, and inline conditional blocks in `right_side_panel.html` and `document.html`
- Per-view construction logic in `views/document.py`, `views/fragment.py`, and `views/toc.py` — each view picks and assembles the pieces differently

PR 62 began consolidating this and introduced regressions (fragment crashes, missing change links, dropped associated documents, mismatched effect taxonomies) — symptoms of the same underlying problem: there is no single place that owns the concept.

Three factors make this more than a tidy-up:

1. **Status messaging is going to get substantially more complex.** Future status surfaces will include collapsibles, fixed-height scrollable sections, and multiple sub-panes within the one status region. The full requirement set is not yet visible.
2. **The client has explicitly asked that this be revisable.** The legislation.gov.uk editorial team must be able to revise both the wording and the logic of status messages without a major rewrite each time.
3. **Welsh translations are required.** Every user-facing string must go through Django's i18n machinery, and status messages contain frequent variable interpolation (document titles, dates, type labels) which complicates this.

The architecture must therefore optimise for **ease of future revision** more than for any particular present-day correctness. Whatever we build will be wrong in detail and we will change course often; the goal is to make change cheap.

## Decision

Introduce a single bounded context for status messaging, consisting of two co-evolving collaborators:

1. **A `status` Python module** that exposes factory methods. Views call a factory with whatever inputs they have (metadata, timeline, etc.) and receive an opaque "status object" in return.
2. **Status-owned rendering templates** that know how to render any object the factory produces. This may be one template or a small owned template family split by placement (for example, main pane and side panel). Status templates are the only templates that introspect the object, and they own all rendering — including all i18n.

Views are dumb pass-through: they construct nothing about status, they introspect nothing about it, they pass the status object to status-owned templates wherever the page layout needs status to render. Everything else — choice of message, taxonomy of effects, conditional layout, translation, date formatting — lives inside the status module and its owned templates.

### What is "the status surface"?

The status object covers the status surfaces on a legislation page: the main status pane above the text, the status material in the side panel, and closely related notices such as the King's Printer message when they render as part of that same reader-facing status region. Adjacent flags and panels currently treated separately ("first and only version" handling, PDF-only status messaging) fold into status if they render in one of those surfaces; if they render elsewhere they remain outside. When a flag is borderline, default to including it — keeping related concepts together is cheaper than enforcing a tight boundary.

### Shape of the status object

The exact object shape is **deliberately not specified** by this ADR beyond the following:

- It is opaque to callers. Views, controllers, and other templates do not introspect it.
- It is a typed Python object — a `dataclass`, not a plain dict. The dataclass constructor catches misspelled fields at construction, and static type checking helps catch shape mistakes before runtime — failures a plain dict would absorb silently. Using `frozen=True` and/or `slots=True` further prevents post-construction attribute typos. Template-side missing variables are a separate concern, addressed under Testing below.
- It carries **data**, not pre-formatted strings.
- The status templates are its only consumers.
- It carries the core facts needed by every status surface: display context, document identity/label/type, up-to-date state, relevant dates, effect groups, links/actions, and any notices.

We start with whatever shape the first factory needs and let the shape evolve as more factories are added. We will refactor toward discriminated kinds, sub-objects, or other structures when patterns emerge — not before.

### i18n lives in the template

The status object carries data: kinds, dates, document type labels, document titles, counts, effect lists. The status templates render that data into prose using `{% translate %}` and `{% blocktranslate %}`. Translators work in one owned template area, not in Python source.

This is the intended direction; we accept that interpolation-heavy strings may make the template messy and reserve the right to revisit if it becomes unworkable in practice. Welsh in particular has consonant mutations (the initial letter of a word changes after certain words and contexts) and a six-form CLDR plural system. Plural counts should still ride through `{% blocktranslate count … %}` and the `.po` file's plural rules — that is exactly what gettext is for, and it handles Welsh's plural categories natively. Where the template hits a wall is on grammar gettext can't reach: the most likely escape hatch is for the factory to pre-compute grammatical labels and forms (a context-appropriate form of a doc-type label, for example) and pass them through, so the translator receives a value rather than being asked to assemble the phrase. The status module may also choose message kinds or small render models that select between translatable template branches. We still avoid returning arbitrary pre-formatted English strings from Python. If we do change course, we change course inside the bounded context — no other code is affected.

### Effect display taxonomy: three-way for now

The current designs appear to combine prospective effects and fixed-future effects, so the initial status surface will display three groups: `outstanding`, `future`, and `unrequired`.

This is a presentational decision, not a permanent domain claim. The old four-way grouping (`outstanding`, `prospective`, `fixedFuture`, `unrequired`) may return if the designs or wording need to distinguish effects with no in-force date from effects with a fixed future date. The taxonomy lives inside the status module and its templates, so that change should be local to two places rather than rippling through views.

## Details

### Module location

A new module `lgu2/status.py` (single file) housing factory methods and any internal helpers. Promote to a package (`lgu2/status/`) when one file becomes unwieldy, not before.

### Template location

A new directory `lgu2/templates/status/` containing the status-owned template or template family. If the page layout needs status in multiple placements, use explicit owned templates such as `status/main.html` and `status/side_panel.html`, or an entry-point template with a placement parameter. Views and layout templates may include status-owned templates, but no non-status template should introspect the status object.

### Factory methods

Each view calls a factory appropriate to its surface — for example `for_document(meta, timeline)`, `for_fragment(meta, timeline)`, `for_toc(meta)`. Different inputs, one status object contract. The factory's job is to normalise its inputs into that contract.

The number of factories is expected to grow as new contexts arise. Adding one is cheap by design.

### Factories are pure functions

Factory methods take their inputs and return a status object. They do not perform I/O — no API calls to the Spring Boot backend, no cache lookups, no file or database access. If a future status feature needs data the view does not currently fetch, the view's existing API call must be extended to provide it; the factory does not silently make a second request.

This slightly tightens the "views are dumb pass-through" framing: views do not construct the status object or introspect it, but they do need to know which inputs the relevant factory requires. That coupling is acceptable. The alternative — factories performing their own I/O — hides performance characteristics inside helpers that are supposed to be cheap, and makes status testable only via integration tests.

### Migration

The existing scattered code remains in place while the new module is built. Views are migrated one at a time — likely document → fragment → ToC. As each view's old code path becomes unreachable, it is deleted with that view's migration. Shared modules and templates that still have remaining callers (`messages/status.py`, the status portions of `helper/status.py`, `status_panel.html`, `up_to_date.html`, the inline status blocks in `right_side_panel.html` and `document.html`) cannot be removed incrementally; they are deprecated during migration and physically deleted in a final cleanup commit once the last view has migrated.

PR 62's status-specific code paths are superseded by this work. Its status bugs (fragment crash, missing `changes_link`, mismatched effect taxonomies, `is_first_and_only_version` split from status rendering, etc.) should be fixed by replacing the affected paths rather than by patching the old shape in place. Non-status regressions from the same PR, such as dropped associated documents or a debug print in a view, still need direct fixes during migration.

## Testing

The architecture separates testable concerns into two clear layers:

- **Factory tests (Python unit).** Factories are pure functions of their inputs (see *Factories are pure functions* above), so they unit-test cleanly. Assertions are on object fields, not on translated prose, which means tests are stable across wording changes and unaffected by Welsh translation work. Coverage of edge cases (no timeline, fragment vs document, prospective effects, etc.) lives here.
- **Template tests (Django render).** A small number of `Client` or `RequestFactory` tests render the status-owned templates against representative status objects and assert on the resulting markup or text. These catch template typos, missing translations, and rendering regressions. They do not need to enumerate every wording variant — that's the factory tests' job.
- **Translation integrity.** Standard `makemessages` / `compilemessages` checks plus `gettext` lint suffice for catching missing or malformed translation strings.

Status template tests should render under a strict template configuration where missing variables surface as a noisy sentinel (e.g. `'!!!INVALID!!!'`) rather than as empty strings. Scope this to the status template tests — applying `string_if_invalid` globally in dev or test settings would affect every other template in the project, some of which intentionally tolerate optional variables, and would inject noise into unrelated tests. The strictness can be contained either by building a dedicated `Template`/`Engine` with strict options inside the status test fixture, or by wrapping the relevant test cases with `@override_settings`. Django's default silent-failure rendering is otherwise the most likely vector for status-rendering bugs reaching production, since Python typing of the status object does not propagate into template attribute lookups.

## Consequences

- **Views become trivial.** They construct status by calling one function and pass the result to the template. The view layer no longer needs to know what status is.
- **Status complexity is contained.** The status module and its owned templates are the only places that need to change as messaging evolves.
- **Revision is cheap.** Editorial changes to wording happen in the template; editorial changes to logic happen in the module. Either can change without affecting the other's interface to the rest of the app.
- **i18n has one home.** Translators work in the status templates. No Python-side gettext calls compete for their attention.
- **Tight coupling between module and templates is intentional.** They co-evolve as a unit. Changing the object shape requires changing both — but only those two areas — and that is the whole point.
- **The templates will absorb conditional logic.** Branching by kind, by document type, by language, by effect category. We accept this; it is where the complexity belongs given the design.
- **Adjacent panels (King's Printer, etc.) move inside.** Anything rendering in a status surface is owned by status. This consolidates concepts that have drifted apart.
- **The status object's shape is unstable by design.** Anything outside the module/templates that reaches into the object will break repeatedly. This is enforced by convention, not by typing.

## Alternatives Considered

- **Schema-first object with a discriminated `kind` union.** Each factory produces an object tagged with a kind; the template dispatches on kind to a sub-template. Cleaner per-kind but commits to a structure before we know whether kinds are mutually exclusive (they may not be — a status pane could combine outstanding effects with a "viewing historical" notice). Rejected for now; we may converge on this once patterns settle.
- **Translate strings in Python (gettext) and pass pre-formatted strings to the template.** Simpler for complex interpolation but splits translators' work across Python and templates, and re-introduces the very pattern PR 62 used (`build_status()` returning `message: "..."`) that this ADR is moving away from. Rejected.
- **Keep four-way effect taxonomy.** Preserves the prospective-vs-fixed-date distinction. Deferred rather than rejected: the taxonomy is internal to the module and can be reinstated without ripple.
- **Several independent status surfaces, several unrelated templates.** Covers a hypothetical world where status appears in multiple places at varying detail. Rejected: the status object should stay single and owned. If placement requires more than one template, those templates should be status-owned and read the same object — or the relevant flag should be computed outside status if it truly renders elsewhere.
- **One entry point that accepts several distinct objects (e.g. legislation status, printer notices, version notices).** Avoids the "junk drawer" risk of a single status object accumulating unrelated concerns. Rejected: the concerns folded in here (King's Printer, PDF status, viewing-context, effects, up-to-date state) all key off the same document metadata fetched in the same API call, with no divergent lifecycle, invalidation rule, or data source. Surface-cohesion becomes a junk drawer when the surface is incidentally shared; here the surface *is* the domain. Splitting into multiple objects would force views to construct and pass several things, partially undoing the architecture's main value of a one-call, one-object contract.
- **Fix PR 62 in place.** Cheaper now but leaves the architectural problem untouched and makes the next round of changes equally painful. Rejected.

## Open Questions

- **Object shape.** Deferred beyond the core facts listed above. We will let the first two or three factories drive the detailed shape and refactor when a pattern is visible.
- **Where do peripheral flags live?** Borderline cases (flags that key off status-related metadata but render outside the status surfaces) can live inside the status object or be computed separately in views. Decide case-by-case; the cost of getting it wrong is low.
- **Template-side i18n complexity.** Heavy interpolation may make `{% blocktranslate %}` blocks unwieldy. We will revisit if the template becomes unreadable; the contract with the rest of the app is unaffected by such a change.

## Delivery Plan

Six commits on `status-branch-jim`, structured so that every commit leaves document, fragment, and ToC pages rendering and the test suite green.

### C1 · Fix PR 62's non-status regressions

- Restore the associated-documents loop in `views/document.py`, populating `explanatory_notes` and `other_associated_doc`.
- Remove `print(data['status'])` from `views/toc.py`.
- Move the misplaced `from datetime import datetime` import to the top of `views/helper/status.py`.

This commit is independent of the new status architecture and keeps later commits focused.

### C2 · Introduce the status architecture scaffold

- Add `lgu2/status.py`.
- Add the initial `StatusObject` dataclass, using `frozen=True` and/or `slots=True`.
- Add `lgu2/templates/status/status.html` as the initial status rendering template, or split immediately into placement-specific status-owned templates if the first migration needs both main-pane and side-panel rendering.
- Add the strict status-template test helper or fixture described in the ADR.
- Add minimal smoke tests for the dataclass and template harness.
- Add Welsh `.po` entries for any strings introduced by the scaffold.

No view should use the new architecture yet. This commit establishes the bounded context and test harness.

### C3 · Migrate the document view

- Add `for_document(meta, timeline)` in `lgu2/status.py`.
- Extend `templates/status/status.html` to render document status states: up-to-date, not-up-to-date, dated-version, King's Printer, and future-effects.
- Fold `make_pdf_status_message` and `is_first_and_only_version` into the status module where they render in the status surface.
- Update `views/document.py` to call `for_document(...)` and pass the resulting status object to the template.
- Update `templates/new_theme/document/document.html` to include the relevant status-owned template(s), e.g. main-pane and side-panel placements.
- Be careful with shared templates such as `right_side_panel.html`: either leave old-path behaviour intact for fragment/ToC, include a status-owned side-panel partial for the migrated document path only, or add temporary dispatch that safely supports both old and new status shapes.
- Add factory unit tests for document status states.
- Add status template render tests using the strict template fixture.

After this commit, document pages use the new architecture. Fragment and ToC still use the old paths.

### C4 · Migrate the fragment view

- Add `for_fragment(meta, timeline)` in `lgu2/status.py`.
- Extend `templates/status/status.html`, or add an owned status sub-template, to handle fragment-shaped status: fragment label, direct effects, ancestor effects, and fragment-specific copy.
- Update `views/fragment.py` to call `for_fragment(...)`.
- Remove the local status-dict construction and the incorrect `status_message` plumbing introduced by PR 62.
- Preserve fragment rendering while any shared templates are still used by ToC.
- Add factory tests for fragment cases, including with and without ancestor effects.
- Add Welsh `.po` entries for any new strings.

After this commit, document and fragment use the new architecture. ToC still uses the old path.

### C5 · Migrate the ToC view

- Add `for_toc(meta)` in `lgu2/status.py`.
- Update `views/toc.py` to call `for_toc(...)`.
- Remove the `make_status_data(meta)` and `make_pdf_status_message(meta)` calls from `views/toc.py`.
- Update `templates/new_theme/document/toc.html` to include the new status entry point and remove old status includes such as `right_side_panel.html`, `status_panel.html`, and `status_message.html` where they are status-specific.
- Add factory tests for ToC cases.
- Add Welsh `.po` entries for any new strings.

After this commit, no view should depend on old status construction.

### C6 · Delete superseded status code

- Delete `lgu2/messages/status.py`. If `lgu2/messages/` becomes empty, remove the package.
- Delete the status-related parts of `lgu2/views/helper/status.py`: `make_status_data`, `make_pdf_status_message`, `group_effects`, `StatusData`, and `StatusEffects`.
- Delete superseded templates such as `lgu2/templates/new_theme/document/status_panel.html` and `up_to_date.html`.
- Remove leftover status residue from `right_side_panel.html`, `document.html`, and `toc.html`.
- Verify with `rg` that deleted symbols have zero remaining references.

This should be a pure cleanup commit with no intended behaviour change.

### Note on shared templates during migration

`right_side_panel.html`, `status_panel.html`, `status_message.html`, and `up_to_date.html` are currently shared across views. Do not break them midway through the migration: either migrate their consumers before stripping status logic from them, or temporarily support both old and new status shapes until C6.
