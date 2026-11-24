"""Audit source-document vintages without changing reported statement values.

Run: python -m quant.tapg_pit_audit
Outputs are additive. Legacy quarterly values remain available for reconciliation,
but their old availability dates must not be used for predictive validation (D-014).
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / 'data/reference'
DOC_PERIOD = {
    'AR 2021.pdf': ('FY2021', 'annual report (operational tables)'),
    'AR_2022.pdf': ('FY2022', 'annual report (operational tables)'),
    'AR_2023.pdf': ('FY2023', 'annual report (operational tables)'),
    'AR_2024.pdf': ('FY2024', 'annual report (operational tables)'),
    'TAPG_-_AR_2025.pdf': ('FY2025', 'annual report (operational tables)'),
    'FinancialStatement-2026-I-TAPG.pdf': ('Q1 2026', 'interim FS'),
    'FinancialStatement-2026-II-TAPG.pdf': ('H1 2026', 'interim FS'),
    'FinancialStatement-2026-III-TAPG.pdf': ('9M 2026', 'interim FS'),
}


def attach_vintage_dates(statements, dates):
    """Date the exact document in hand, not the fiscal period reproduced in it."""
    dates = dates.set_index(['period', 'disclosure'])
    rows = []
    for r in statements.to_dict('records'):
        key = DOC_PERIOD.get(r['source_doc'])
        if key is None or key not in dates.index:
            available, status = None, 'UNKNOWN_SOURCE_DOCUMENT_DATE'
        else:
            d = dates.loc[key]
            available = d['available_from']
            status = ('SOURCE_DOCUMENT_SECONDARY_TIMESTAMP' if pd.notna(d['idx_timestamp_wib'])
                      else 'ASSUMED_SOURCE_DOCUMENT_DATE_NOT_VALIDATED')
        r.update(source_available_from=available, vintage_status=status,
                 original_period_value_verified=False)
        rows.append(r)
    return pd.DataFrame(rows)


def derive_quarters(vintages):
    """Preserve legacy selected values; date each result to latest contributing source."""
    s = vintages[vintages.status == 'extracted'].drop_duplicates(['item', 'period'], keep='last')
    s = s.set_index(['item', 'period'])
    old = pd.read_csv(REF / 'TAPG_quarterly_derived.csv')
    rows = []
    for r in old.to_dict('records'):
        year, q = r['quarter'][:4], int(r['quarter'][-1])
        labels = {1: [f'Q1 {year}'], 2: [f'H1 {year}', f'Q1 {year}'],
                  3: [f'9M {year}', f'H1 {year}'], 4: [f'FY{year}', f'9M {year}']}[q]
        inputs = [s.loc[(r['item'], label)] for label in labels]
        known = all(pd.notna(x.source_available_from) for x in inputs)
        dates = [pd.Timestamp(x.source_available_from) for x in inputs] if known else []
        available = max(dates).date().isoformat() if dates else None
        original = r.pop('available_from')
        r.update(legacy_available_from=original, available_from=available,
                 inputs='; '.join(f'{x.source_doc} p{int(x.pdf_page)} ({label})' for label, x in zip(labels, inputs)),
                 available_basis='LATEST_CONTRIBUTING_SOURCE_DOCUMENT',
                 date_moved_later=bool(available and available > original),
                 pit_validated=False)
        rows.append(r)
    return pd.DataFrame(rows)


def main():
    vintages = attach_vintage_dates(pd.read_csv(REF / 'TAPG_statements_extracted.csv'),
                                   pd.read_csv(REF / 'TAPG_disclosure_dates.csv'))
    vintages.to_csv(REF / 'TAPG_statement_vintages.csv', index=False)
    q = derive_quarters(vintages)
    q.to_csv(REF / 'TAPG_quarterly_vintage_safe.csv', index=False)
    checks = []
    for f in sorted(REF.glob('*checks.csv')):
        d = pd.read_csv(f)
        if 'result' in d:
            for result, n in d.result.value_counts().items():
                checks.append(dict(file=f.name, result=result, rows=n))
    pd.DataFrame(checks).to_csv(REF / 'research/checkpoint_validation_counts.csv', index=False)
    print(f'Quarterly dates moved later: {q.date_moved_later.sum()}/{len(q)}; numeric values unchanged.')


if __name__ == '__main__':
    main()
