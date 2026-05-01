# Status messages

Authoritative prose for each status-messaging case. Each top-level item
is one case; the nested bullet(s) underneath give the exact text the
status module must render.

Checkboxes indicate implementation state in `lgu2/status.py`:

- `[ ]` — pending implementation
- `[x]` — implemented and renders correctly
- `[~]` — cannot implement yet

When the client revises a message's prose, uncheck the box until the
implementation catches up.

---

[ ] Directives
  - EU Directives are published on this site to aid cross referencing from UK legislation. Since IP completion day (31 December 2020 11.00 p.m.) no amendments have been applied to this version.

[ ] Not UKamended
  - This version of this Decision was derived from [EUR-Lex](https://eur-lex.europa.eu/homepage.html) on IP completion day (31 December 2020 11:00 p.m.). It has not been amended by the UK since then. [Find out more about legislation originating from the EU as published on legislation.gov.uk](https://www.legislation.gov.uk/eu-legislation-and-uk-law).

[~] Bank of England *(awaiting prose)*

[~] Direct Payments to Farmers *(awaiting prose)*

[~] Treaties *(awaiting prose)*

[ ] Up to date
  - There are currently no known outstanding effects by UK legislation for Commission Implementing Decision (EU) 2020/2239.

[ ] ToC red
  - There are outstanding changes by UK legislation not yet made to Commission Delegated Regulation (EU) No 640/2014. Those changes will be listed when you open the content using the Table of Contents below. Any changes that have already been made to the legislation appear in the content and are referenced with annotations.

[ ] ToC green
  - There are currently no known outstanding effects by UK legislation for Regulation (EU) No 528/2012 of the European Parliament and of the Council.

[ ] ToC prosp
  - Statutory Instruments Act 1946 is up to date with all changes known to be in force on or before 21 January 2026\. There are changes that may be brought into force at a future date.

[ ] Prosp effects not yet in-force
  - Regulatory Enforcement and Sanctions Act 2008, Cross Heading: Establishment of LBRO is up to date with all changes known to be in force on or before 22 January 2026\. There are changes that may be brought into force at a future date. Changes that have been made appear in the content and are referenced with annotations.

[ ] Standard green
  - There are currently no known outstanding effects for the Neighbourhood Planning Act 2017, Section 17

  > Note: this prose is for the main status pane. The side panel renders
  > a shorter equivalent — *"{Title} is up to date with all known
  > changes"* — taken from the design rather than this catalog. The
  > catalog text was not intended for a narrow-column side panel.

[x] Standard red
  - There are outstanding changes not yet made by the legislation.gov.uk editorial team to Act of Sederunt (Rules of the Court of Session 1994) 1994. Any changes that have already been made by the team appear in the content and are referenced with annotations

[~] Document with future-effects but no outstanding effects *(awaiting design — when a document is up-to-date but has required effects with a future commencement date (`required=True`, `outstanding=False`), the legacy frontend rendered a separate "changes and effects yet to be applied" panel on the main pane. The new design samples on http://johngoodall.com/tna/mvp/ have no equivalent panel for this case on the document main pane. Implementing this requires either a design sample to follow or new catalog prose plus structure.)*

[~] Fragment with separately rendered direct vs ancestor effects *(awaiting design — the API returns outstanding effects on a fragment in two groups: those that target the fragment itself (or its descendants) and those that target an ancestor (e.g. a chapter containing the section being viewed). The legacy frontend rendered the two groups under separate sub-panels with their own headings. The new design samples on http://johngoodall.com/tna/mvp/ show only one flat list inside the disclosure on fragment pages, with no sub-headings or grouping, and the new-theme CSS contains no rules for sub-headings or nested lists inside the status disclosure. Until designs and CSS catch up, C4 concatenates direct + ancestor outstanding effects into one flat list so neither group is silently dropped. When grouped designs arrive, the change is local to the fragment factory and the disclosure rendering.)*

[ ] Omitted ([https://www.legislation.gov.uk/uksi/2014/3348/article/4)](https://www.legislation.gov.uk/uksi/2014/3348/article/4\))
  - This version of this provision no longer has effect.

[ ] Superseeded
  - Point in time view as at 29/09/2021. This version of this provision has been superseded

[x] Original
  - This is the original version (as it was originally made).

[ ] PDF only
  - This item of legislation is only available to download and view as PDF.

[~] Contributor – Westlaw *(awaiting prose)*

[~] Contributor – British History Online *(awaiting prose)*

[ ] Draft not superseded
  - This is a draft item of legislation and has not yet been made as a UK Statutory\[Scottish Statutory Instrument\]\[Northern Ireland Statutory Rule\] Instrument.

[ ] Draft superseded
  - This is a draft item of legislation. This draft has since been made as a UK Statutory Instrument\[Scottish Statutory Instrument\]\[Northern Ireland Statutory Rule\]: The Rehabilitation of Offenders Act 1974 (Exceptions) (Amendment) (England and Wales) Order 2026 No…

[~] Custom message *(awaiting prose — like quashed, or others above)*

[ ] Impact Assessments
  - This is the Post Implementation\[Final\]\[etc.\] version of the Impact Assessment.
  - This impact assessment is only available to download and view as PDF.

[ ] Draft Explanatory Memorandum
  - This is a draft Memorandum to accompany this Northern Ireland Draft Statutory Rules

[ ] Explanatory Memorandum
  - This Memorandum is only available to download and view as PDF.

[ ] No revised
  - This is the original version (as it was originally made). This item of legislation is currently only available in its original format.
