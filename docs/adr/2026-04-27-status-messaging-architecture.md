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

1. **A `status` Python module** that exposes factory methods. Views call a factory with whatever inputs they have (metadata, timeline, etc.) and receive an opaque "status object" in return. The module owns status-message selection and translated prose assembly.
2. **Status-owned rendering templates** that know how to render any object the factory produces. This may be one template or a small owned template family split by placement (for example, main pane and side panel). Status templates are the only templates that introspect the object, and they own generic component rendering.

Views are dumb pass-through: they construct nothing about status, they introspect nothing about it, they pass the status object to status-owned templates wherever the page layout needs status to render. Everything else — choice of message, taxonomy of effects, translated prose, date formatting, and generic component rendering — lives inside the status module and its owned templates.

### The contract runs template-first

The contract between these two collaborators runs **template-first**: the status templates define the presentation primitives they consume — panels, labels, tones, optional disclosures, lists — and the factory's job is to satisfy that contract. The status object is a presentation DTO, not a domain object dressed for rendering.

The controller speaks meaning; CSS speaks pixels. The object carries semantic primitives such as `severity: "warning"` or `tone: "muted"`, never literal style props like `border_color` or `padding_px`. Visual realisation belongs to the stylesheet, not the backend.

New UI variants therefore begin in the template — sketch the generic markup the design calls for, read the component contract off the placeholder references, and add fields to the object only when the template asks for them. The template becomes the source of truth for what UIs are possible, while the factory remains responsible for deciding which translated prose fills those UI primitives.

### What is "the status surface"?

The status object covers the status surfaces on a legislation page: the main status pane above the text, the status material in the side panel, and closely related notices such as the King's Printer message when they render as part of that same reader-facing status region. Adjacent flags and panels currently treated separately ("first and only version" handling, PDF-only status messaging) fold into status if they render in one of those surfaces; if they render elsewhere they remain outside. When a flag is borderline, default to including it — keeping related concepts together is cheaper than enforcing a tight boundary.

### Scope of this migration

The presentation-model pattern naturally extends beyond status to other component surfaces, including the document right-side panel. This migration applies the pattern only to the status surface. Existing page/layout templates may remain domain-aware while they compose status with adjacent panels such as extent, in-force, confers-power, and blanket-amendments. Migrating those surfaces to their own presentation models is future work.

### Scope of catalog cases covered

`docs/status_messages.md` enumerates roughly 25 messaging cases. This migration covers only **Original** and **Standard red** — the two cases the legacy site currently produces — plus their fragment and ToC variants, and the dated-version side panel that accompanies non-current views of those documents. All other catalog cases remain `[ ]` or `[~]` and are out of scope until separately commissioned.

The architecture is built so that adding a further case later is local: a new branch in the relevant factory, possibly new catalog prose, and reuse of the existing presentation primitives in `templates/status/`. Adding cases should not require revisiting this ADR.

### Shape of the status object

The shape is **derived from the template**, not designed up front. We do not specify it in this ADR beyond the following invariants:

- It is opaque to callers. Views, controllers, and other templates do not introspect it.
- It is a typed Python object — a `dataclass`, not a plain dict. The dataclass constructor catches misspelled fields at construction, and static type checking helps catch shape mistakes before runtime — failures a plain dict would absorb silently. Using `frozen=True` and/or `slots=True` further prevents post-construction attribute typos. Template-side missing variables are a separate concern, addressed under Testing below.
- It carries **presentation data**, including translated strings assembled by the status module for generic templates to render.
- It carries **semantic** primitives, not literal style props (see *The contract runs template-first* above).
- The status templates are its only consumers.

The shape grows out of the templates being written. Sketch the template the factory will feed first; the fields the object needs to expose are exactly the ones the template references. We refactor toward discriminated kinds, sub-objects, or other structures only when patterns emerge across multiple templates — never as up-front design.

### i18n lives in the status module

The status object carries presentation components: headings, body text, labels, disclosures, links, lists, and semantic tones. The status module assembles the prose for those components using Django's Python-side i18n APIs (`gettext`, `ngettext`, `pgettext`, etc.) before handing the object to generic templates.

This is a deliberate change from template-side prose assembly. Generic status templates should know how to render a `Message`, `Disclosure`, or similar component; they should not know the legislation-specific sentence patterns that decide what those components say. That keeps template branching focused on component structure and keeps wording, interpolation, pluralisation, and grammar decisions beside the status logic that chooses the message.

Welsh in particular has consonant mutations (the initial letter of a word changes after certain words and contexts) and a six-form CLDR plural system. Python-side gettext still uses the same `.po` files and plural rules as template gettext, so plural counts should use `ngettext` or related APIs rather than hand-built English branches. Where gettext alone cannot express a grammatical form, the status module may pre-compute context-specific labels and choose the appropriate translated message.

### Effect display taxonomy: outstanding only, flat list, for now

The new design samples (http://johngoodall.com/tna/mvp/) render a single flat list of effects inside the not-up-to-date disclosure, with no group headings. We match this: the disclosure shows only `outstanding=True` effects, in API source order, with no `Outstanding` / `Fixed Future` / `Unrequired` sub-sections.

Two consequences worth naming:

1. **Future-effects-only documents are deferred.** When a document is up-to-date but has required, not-yet-in-force effects (`required=True, outstanding=False`), the legacy frontend rendered a separate "changes and effects yet to be applied" panel on the main pane. The new designs have no equivalent. Implementing this case requires either a design sample or new catalog prose plus structure. Tracked in `docs/status_messages.md` as *"Document with future-effects but no outstanding effects"* with a `[~]` (cannot implement yet) marker.
2. **The taxonomy decision is provisional.** If a future design reintroduces grouped effects (`Outstanding` / `Fixed Future` / `Unrequired` subheadings) or a separate future-effects panel, the change is local to the status module and its disclosure rendering, with no ripple into views.

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

- **Factory tests (Python unit).** Factories are pure functions of their inputs (see *Factories are pure functions* above), so they unit-test cleanly. Assertions are on selected components, labels, links, tones, and representative translated text where useful. Coverage of edge cases (no timeline, fragment vs document, prospective effects, etc.) lives here.
- **Template tests (Django render).** A small number of `Client` or `RequestFactory` tests render the status-owned templates against representative status objects and assert on the resulting markup or text. These catch template typos and rendering regressions. They do not need to enumerate every wording variant — that's the factory tests' job.
- **Translation integrity.** Standard `makemessages` / `compilemessages` checks plus `gettext` lint suffice for catching missing or malformed translation strings.

Status template tests should render under a strict template configuration where missing variables surface as a noisy sentinel (e.g. `'!!!INVALID!!!'`) rather than as empty strings. Scope this to the status template tests — applying `string_if_invalid` globally in dev or test settings would affect every other template in the project, some of which intentionally tolerate optional variables, and would inject noise into unrelated tests. The strictness can be contained either by building a dedicated `Template`/`Engine` with strict options inside the status test fixture, or by wrapping the relevant test cases with `@override_settings`. Django's default silent-failure rendering is otherwise the most likely vector for status-rendering bugs reaching production, since Python typing of the status object does not propagate into template attribute lookups.

## Consequences

- **Views become trivial.** They construct status by calling one function and pass the result to the template. The view layer no longer needs to know what status is.
- **Status complexity is contained.** The status module and its owned templates are the only places that need to change as messaging evolves.
- **Revision is cheap.** Editorial changes to wording and logic happen in the status module. Structural changes to status UI happen in status templates. Either can change without affecting the interface to the rest of the app.
- **i18n has one home.** Status-message translation strings live in the status module. Templates may still translate generic component chrome if needed, but legislation-specific prose belongs beside the factory logic that chooses it.
- **Tight coupling between module and templates is intentional.** They co-evolve as a unit. Changing the object shape requires changing both — but only those two areas — and that is the whole point.
- **Templates stay generic.** They branch on component structure, not legislation domain state. Branching by kind, document type, language, and effect category belongs in the status module unless it is genuinely a rendering concern.
- **Adjacent panels (King's Printer, etc.) move inside.** Anything rendering in a status surface is owned by status. This consolidates concepts that have drifted apart.
- **The status object's shape is unstable by design.** Anything outside the module/templates that reaches into the object will break repeatedly. This is enforced by convention, not by typing.

## Alternatives Considered

- **Schema-first object with a discriminated `kind` union.** Each factory produces an object tagged with a kind; the template dispatches on kind to a sub-template. This inverts the contract direction adopted above — schema first, template second — and lets the factory's domain model dictate what the UI can express. Rejected: the design is template-first, and committing to a Python-side `kind` union before any template exists would constrain the templates by a shape that has no UI requirement behind it. If kind-tagging emerges as a useful pattern after templates are written, it can be added then, on top of fields the templates already need.
- **Assemble prose in templates with `{% translate %}` / `{% blocktranslate %}`.** Keeps all template-visible text in templates, but makes generic status components responsible for legislation-specific sentence patterns and complex interpolation. Rejected: the current design keeps templates generic and lets the status module assemble translated prose before rendering.
- **Keep four-way effect taxonomy.** Preserves the prospective-vs-fixed-date distinction. Deferred rather than rejected: the taxonomy is internal to the module and can be reinstated without ripple.
- **Several independent status surfaces, several unrelated templates.** Covers a hypothetical world where status appears in multiple places at varying detail. Rejected: the status object should stay single and owned. If placement requires more than one template, those templates should be status-owned and read the same object — or the relevant flag should be computed outside status if it truly renders elsewhere.
- **One entry point that accepts several distinct objects (e.g. legislation status, printer notices, version notices).** Avoids the "junk drawer" risk of a single status object accumulating unrelated concerns. Rejected: the concerns folded in here (King's Printer, PDF status, viewing-context, effects, up-to-date state) all key off the same document metadata fetched in the same API call, with no divergent lifecycle, invalidation rule, or data source. Surface-cohesion becomes a junk drawer when the surface is incidentally shared; here the surface *is* the domain. Splitting into multiple objects would force views to construct and pass several things, partially undoing the architecture's main value of a one-call, one-object contract.
- **Fix PR 62 in place.** Cheaper now but leaves the architectural problem untouched and makes the next round of changes equally painful. Rejected.

## Open Questions

- **Where do peripheral flags live?** Borderline cases (flags that key off status-related metadata but render outside the status surfaces) can live inside the status object or be computed separately in views. Decide case-by-case; the cost of getting it wrong is low.
- **Future-effects-only main-pane panel.** The legacy frontend rendered a separate "changes and effects yet to be applied" panel for documents that are up-to-date but have required-not-yet-in-force effects. The new design samples are silent on this case. We need either a design sample or new catalog prose to wire it, or an explicit decision to drop the panel. Until then, this case shows nothing on the main pane (the side panel still renders the up-to-date variant correctly).

## Delivery Plan

Six commits on `status-branch-jim`, structured as reviewable development checkpoints rather than independently shippable releases. The branch should keep the test suite green and avoid crashes throughout, but individual checkpoints may contain explicitly documented temporary inconsistencies while a shared surface is between migrations. Nothing should be treated as ready to ship until the ADR's delivery plan is complete.

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

Per the template-first contract, the order matters: sketch the templates first, read the contract off them, then build the factory.

Scope is limited to the catalog cases listed under *Scope of catalog cases covered* (Original, Standard red, and the dated-version side panel for non-current document views).

- Sketch the document main-pane and side-panel status templates in `templates/status/` from the agreed designs. Use placeholder context references (`{{ status.X }}`, `{% for panel in status.panels %}…`, etc.) for whatever the templates need; do not commit to field names beyond what the sketch dictates.
- Read the contract off the sketches: every variable and field the templates reference is, by construction, what the status object must provide. Note the semantic primitives (e.g. `severity`, `tone`) so the object does not slip into literal style props.
- Define the `StatusObject` dataclass to satisfy that contract. The fields exist because the template asked for them.
- Add `for_document(meta, timeline)` in `lgu2/status.py` to construct the object from view inputs.
- PDF-only documents are out of scope per the rescope (catalog entry `[ ] PDF only`); leave the legacy `make_pdf_status_message` path untouched and have `for_document` return `None` for them so the two paths do not double up.
- Update `views/document.py` to call `for_document(...)` and pass the resulting status object to the template.
- Update `templates/new_theme/document/document.html` to include the relevant status-owned template(s).
- Be careful with shared templates such as `right_side_panel.html`: either leave old-path behaviour intact for fragment/ToC, include a status-owned side-panel partial for the migrated document path only, or add temporary dispatch that safely supports both old and new status shapes.
- It is acceptable in this commit for the shared ToC right-side panel include to remain temporarily inconsistent with the document status path. C3 migrates the document status surface only; ToC right-side-panel status rendering is picked up in C5.
- Add factory unit tests for document status states.
- Add status template render tests using the strict template fixture.
- Note: the main-pane "future-effects only" case (`required=True, outstanding=False`) is deferred — see *Effect display taxonomy* and the `[~]` entry in `docs/status_messages.md`.

After this commit, document pages use the new architecture. Fragment and ToC still use the old paths.

### C4 · Migrate the fragment view

Same template-first sequence as C3. Scope is the fragment variants of Original and Standard red — see *Scope of catalog cases covered*.

- Sketch the fragment-shaped status template (or sub-template) for handling fragment label, direct effects, ancestor effects, and fragment-specific copy. Use placeholder references for whatever the design needs.
- Read the contract off the sketch and extend `StatusObject` (or introduce sub-objects) with whatever the template references. Stay semantic.
- Add `for_fragment(meta, timeline)` in `lgu2/status.py` to satisfy the new contract.
- Update `views/fragment.py` to call `for_fragment(...)`.
- Remove the local status-dict construction and the incorrect `status_message` plumbing introduced by PR 62.
- Preserve fragment rendering while any shared templates are still used by ToC.
- Add factory tests for fragment cases, including with and without ancestor effects.
- Add Welsh `.po` entries for any new strings.

After this commit, document and fragment use the new architecture. ToC still uses the old path.

### C5 · Migrate the ToC view

Same template-first sequence as C3. Scope is the ToC variants of Original and Standard red — see *Scope of catalog cases covered*.

- Sketch the ToC-shaped status template from the agreed designs, with placeholder references for whatever the ToC surface needs.
- Read the contract off the sketch and extend `StatusObject` (or introduce sub-objects) accordingly.
- Add `for_toc(meta)` in `lgu2/status.py` to satisfy that contract.
- Update `views/toc.py` to call `for_toc(...)`.
- Remove the `make_status_data(meta)` and `make_pdf_status_message(meta)` calls from `views/toc.py`.
- Update `templates/new_theme/document/toc.html` to include the new status entry point and remove old status includes such as `right_side_panel.html`, `status_panel.html`, and `status_message.html` where they are status-specific.
- Resolve the temporary C3 inconsistency in the ToC right-side panel by giving ToC the status-side-panel data it needs or by routing ToC through its own status-owned side-panel entry point.
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

`right_side_panel.html`, `status_panel.html`, `status_message.html`, and `up_to_date.html` are currently shared across views. For a shippable state, do not leave those shared templates broken: either migrate their consumers before stripping status logic from them, or temporarily support both old and new status shapes until C6. During the staged branch work, a checkpoint may deliberately narrow a shared template to the migrated surface only, provided the inconsistency is named in the relevant commit plan and resolved by the later checkpoint that migrates the remaining consumer.
