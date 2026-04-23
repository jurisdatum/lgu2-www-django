from dataclasses import dataclass


@dataclass(frozen=True)
class SummaryClause:
    """A single segment of the changes query summary."""
    key: str
    text: str


@dataclass(frozen=True)
class ChangesSummary:
    """Structured summary of a changes query, for both detail and form contexts."""
    detail_intro: str
    detail_clauses: tuple[SummaryClause, ...]
    form_initial: dict[str, str]


APPLIED_LABELS = {
    'applied': ('Changes that have been applied to the text', 'of'),
    'unapplied': ('Changes not yet applied to the text', 'of'),
}
DEFAULT_APPLIED_LABEL = ('All changes', 'to')


def build_changes_summary(form_values: dict, types: dict) -> ChangesSummary:
    """Build a structured summary from form values and type labels."""
    applied = form_values.get('applied')
    label, connector = APPLIED_LABELS.get(applied, DEFAULT_APPLIED_LABEL)

    affected_type_label = types.get(form_values.get('affected_type', ''), 'any legislation')
    affecting_type_label = types.get(form_values.get('affecting_type', ''), 'any legislation')

    affected_year = _year_text(form_values, 'affected')
    affecting_year = _year_text(form_values, 'affecting')

    clauses = [
        SummaryClause('show_changes', f' {label} {connector}'),
    ]
    clauses.extend(_side_clauses(form_values, 'affected', affected_type_label, affected_year))
    clauses.append(SummaryClause('made_by', ', made by'))
    clauses.extend(_side_clauses(form_values, 'affecting', affecting_type_label, affecting_year))

    form_initial = {
        'showChanges': f'{label} {connector}',
        **_side_form_initial(form_values, 'affected', affected_type_label, affected_year),
        **_side_form_initial(form_values, 'affecting', affecting_type_label, affecting_year),
    }

    return ChangesSummary(
        detail_intro='for',
        detail_clauses=tuple(clauses),
        form_initial=form_initial,
    )


def _side_clauses(form_values: dict, prefix: str, type_label: str, year: str) -> list[SummaryClause]:
    clauses = [SummaryClause(f'{prefix}_type', f' {type_label}')]
    if form_values.get(f'{prefix}_title'):
        clauses.append(SummaryClause(f'{prefix}_title',
                                     f' with the title \u201c{form_values[f"{prefix}_title"]}\u201d'))
    if year:
        clauses.append(SummaryClause(f'{prefix}_year',
                                     f', enacted or made {year}'))
    if form_values.get(f'{prefix}_number'):
        clauses.append(SummaryClause(f'{prefix}_number',
                                     f', with the number \u201c{form_values[f"{prefix}_number"]}\u201d'))
    return clauses


def _side_form_initial(form_values: dict, prefix: str, type_label: str, year: str) -> dict[str, str]:
    # JS expects camelCase keys like affectedType, affectingTitle
    return {
        f'{prefix}Type': type_label,
        f'{prefix}Title': form_values.get(f'{prefix}_title', ''),
        f'{prefix}Year': year,
        f'{prefix}Number': form_values.get(f'{prefix}_number', ''),
    }


def _year_text(form_values: dict, prefix: str) -> str:
    year = form_values.get(f'{prefix}_year')
    start = form_values.get(f'{prefix}_start_year')
    end = form_values.get(f'{prefix}_end_year')
    if year:
        return f'in {year}'
    if start and end:
        if start == end:
            return f'in {start}'
        return f'between {start} and {end}'
    if start:
        return f'from {start}'
    if end:
        return f'to {end}'
    return ''
