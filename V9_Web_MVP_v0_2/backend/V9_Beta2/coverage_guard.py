"""Partner-period coverage metadata; never changes raw totals or store scores."""
from dataclasses import dataclass
import pandas as pd
from data_pipeline import period_row, present

NOT_COMPARABLE = 'Not comparable — incomplete store coverage'


def add_store_coverage(data):
    history = data.store_monthly
    first_seen = history.groupby('Store ID')['Period'].min()
    records = []
    for period in pd.date_range(history.Period.min(), data.reporting_period, freq='MS'):
        expected = set(first_seen[first_seen <= period].index)
        observed = set(history.loc[history.Period == period, 'Store ID'])
        missing = sorted(expected - observed)
        past = history[history.Period <= period].sort_values('Period')
        names = past.drop_duplicates('Store ID', keep='last').set_index('Store ID')['Store Address Address'].to_dict()
        records.append({'Period': period, 'Expected Stores': len(expected), 'Present Stores': len(observed),
                        'Missing Stores': len(missing), 'Missing Store IDs': ' | '.join(missing),
                        'Missing Store Names': ' | '.join(str(names[x]) for x in missing),
                        'Store Coverage Status': 'Partial Store Coverage' if missing else 'Complete Store Coverage'})
    data.coverage = pd.DataFrame(records)
    cols=[c for c in data.coverage if c != 'Period']
    data.monthly=data.monthly.drop(columns=cols,errors='ignore').merge(data.coverage,on='Period',how='left')


@dataclass(frozen=True)
class Comparison:
    current: pd.Timestamp
    previous: pd.Timestamp
    comparable: bool
    reason: str


def comparison(data, current, previous):
    current, previous = pd.Timestamp(current), pd.Timestamp(previous)
    coverage=[period_row(data.coverage, p) for p in (current,previous)]
    if any(r is not None and r['Missing Stores'] > 0 for r in coverage):
        return Comparison(current,previous,False,NOT_COMPARABLE)
    if any(r is None for r in coverage):
        return Comparison(current,previous,False,'Comparison unavailable — period absent')
    return Comparison(current,previous,True,'Comparable store coverage')


def guarded_previous(data, current, months=1):
    prev=current-pd.DateOffset(months=months)
    return period_row(data.monthly,prev) if comparison(data,current,prev).comparable else None


def comparison_exports(data):
    rows=[]
    for current in data.monthly.Period:
        for kind,months in [('MoM',1),('YoY',12)]:
            c=comparison(data,current,current-pd.DateOffset(months=months))
            row={'Period':current,'Comparison':kind,'Reference Period':c.previous,
                 'Comparable':c.comparable,'Reason':c.reason}
            now,before=period_row(data.monthly,current),period_row(data.monthly,c.previous)
            for col in ('€ GMV','# Delivered Orders','Sessions Store','Number of Total Orders','€ AOV Derived','% CVR','% PNA Orders','% Cancels DTP','% Uptime'):
                value=None
                if c.comparable and before is not None and present(now[col]) and present(before[col]):
                    value=(now[col]-before[col]) if col.startswith('%') else now[col]/before[col]-1 if before[col]!=0 else None
                row[col+' Change']=value
            rows.append(row)
    return pd.DataFrame(rows)


def coverage_summary(data,period):
    r=period_row(data.coverage,period)
    if r is None: return 'Store coverage unavailable'
    return f"{r['Store Coverage Status']} · Expected {r['Expected Stores']} · Present {r['Present Stores']} · Missing {r['Missing Stores']}"
