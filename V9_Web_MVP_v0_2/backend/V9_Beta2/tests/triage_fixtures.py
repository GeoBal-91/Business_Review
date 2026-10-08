"""Contract fixtures: synthetic completions of partial brief controls, not recovered real partner rows.

Only supplied fields / human labels are evidence. Scores in contract_case are
injected inputs to the new triage layer, NOT claimed frozen-engine reproductions.
Generated UX fixtures below always use actual unmodified engine scores.
"""
from datetime import date
from dataclasses import replace
from copy import deepcopy
import pandas as pd
from analysis import analyze
from config import Settings
from data_pipeline import load_frames, G, D, N, T, P, C, U
from test_regression import fixture, zero, run


def engine_case(sbu='PETS', *, stores=2, sessions=90, attempts=20, cvr=.02, pna=.4, cancels=.05, uptime=.80,
                gmv=100, delivered=5, benchmark_cvr=.2, benchmark_pna=.08, benchmark_cancels=.025):
    primary = fixture('Control', **{'Store Address Address': 'Synthetic control store', 'Store Sub Business Unit': sbu,
                        G: gmv, D: delivered, N: sessions, T: attempts, P: round(attempts*pna), C: round(attempts*cancels),
                        '% CVR': cvr, U: uptime})
    rows = [primary]
    rows += [fixture(f'Other-{i}', **{'Store Sub Business Unit': sbu, G: 15000, N: 1000, D: 200,
                   T: 400, P: 32, C: 10, U: .98, '% CVR': .2}) for i in range(stores - 1)]
    benchmark = fixture(**{'Store Sub Business Unit': sbu, N: 10000, T: 1000, P: benchmark_pna*1000,
                           C: benchmark_cancels*1000, '% CVR': benchmark_cvr, G: 500000})
    return analyze(load_frames(pd.DataFrame(rows), pd.DataFrame([benchmark]), Settings(partner_sbu=sbu, as_of_date=date(2026,9,13))))


def contract_case(priority=4.24, primary=None, **kwargs):
    a = engine_case(**kwargs)
    idx = a.stores.index[a.stores['Store ID'] == 'Control'][0]
    a.stores.loc[idx, 'Opportunity Score'] = priority
    # Contract-level raw observations may be quoted rounded rates in the brief.
    # Inject them explicitly after a valid synthetic engine run; this is not a real-input replay.
    for metric, key, column in [('PNA','pna','% PNA Orders'),('Cancels','cancels','% Cancels DTP')]:
        if key in kwargs:
            a.stores.loc[idx,column]=kwargs[key]
            a.metrics.loc[(a.metrics['Store ID']=='Control') & (a.metrics['metric']==metric),'raw_rate']=kwargs[key]
    if primary:
        a.stores.loc[idx, 'Main Driver'] = primary
    # Original opportunity/action rows intentionally left unchanged: tests must prove no mutation.
    return a


def flowers_ten():
    """Synthetic coverage of the requested 1/2/3/4 class mix; not the unseen human dataset."""
    rows = [fixture('Action', **{N: 10000, '% CVR': .01, U: .626}),
            fixture('Monitor-1', **{N: 100, '% CVR': .1, U: .1}),
            fixture('Monitor-2', **{N: 100, '% CVR': .12, U: .2})]
    rows += [fixture('Healthy-' + str(i), **{U: .4 if i == 0 else .95}) for i in range(3)]
    rows += [zero('Inactive-' + str(i)) for i in range(4)]
    for row in rows:
        row['Store Sub Business Unit'] = 'FLOWERS'
    benchmark = fixture(**{'Store Sub Business Unit': 'FLOWERS', G: 500000})
    return analyze(load_frames(pd.DataFrame(rows), pd.DataFrame([benchmark]), Settings(partner_sbu='FLOWERS', as_of_date=date(2026,9,13))))


def new_visual_fixtures():
    return [
        ('Multi_KPI', engine_case()),
        ('Single_Store', engine_case(sbu='VAPES', stores=1)),
        ('Severe_CVR_Corroboration', engine_case(sbu='ELECTRONICS', sessions=84, attempts=3, delivered=1, pna=1/3, cancels=1/3, uptime=.922)),
        ('Materiality', engine_case(sbu='HOME_DECORATION', sessions=500, attempts=160, delivered=80, cvr=.2,
                                   pna=.23, cancels=.15, uptime=.897, gmv=6708, benchmark_pna=.149, benchmark_cancels=.094)),
        ('FLOWERS_Ten', flowers_ten()),
        ('Pharmacy_Ultra_Low', engine_case(sbu='PHARMACY_OTC', sessions=90, attempts=5, delivered=2, gmv=14, cvr=.02, uptime=.80)),
    ]
