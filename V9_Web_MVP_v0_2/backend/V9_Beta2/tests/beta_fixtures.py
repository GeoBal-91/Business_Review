"""Explicit synthetic Beta UX inputs. All results pass through the frozen engine."""
from datetime import date
from dataclasses import replace
import numpy as np
import pandas as pd
from config import Settings
from analysis import analyze
from data_pipeline import load_frames, G, D, N, T, P, C, U
from test_regression import fixture, zero, run
from presentation_hardening_fixtures import recommendation_rich, current_partial, no_recommendations


def flowers():
    rows = [fixture('Flowers Central', month, **{U: .3 if month == 'August' else .98,
                         N: 14000, '% CVR': .02, 'Store Address Address': '12 Flower Market Street, Tbilisi'})
            for month in ['March', 'April', 'May', 'June', 'July', 'August']]
    s = Settings(partner_sbu='FLOWERS', as_of_date=date(2026, 9, 7))
    benchmarks = [fixture(month=m, **{'Store Sub Business Unit': 'FLOWERS'})
                  for m in ['March', 'April', 'May', 'June', 'July', 'August']]
    return analyze(load_frames(pd.DataFrame(rows), pd.DataFrame(benchmarks), s))


def large_partner(n=30):
    rows = []
    streets = ['Rustaveli Avenue', 'Chavchavadze Avenue', 'Abashidze Street', 'Pekini Avenue',
               'Vazha-Pshavela Avenue', 'Tsereteli Avenue']
    months = ['March', 'April', 'May', 'June', 'July', 'August']
    for i in range(n):
        sid = f'BETA-{i+1:02}'
        for month in months:
            fields = {'Store Name': f'Synthetic Branch {i+1:02}',
                      'Store Address Address': f'{10+i} {streets[i%6]}, Tbilisi, Georgia',
                      G: 2000+i*311, N: 5000+i*275, D: 200+i*10, T: 500+i*15,
                      P: 110 if i%7 == 0 else 32, C: 100 if i%8 == 0 else 10,
                      '% CVR': .025+i*.003 if i < 6 else .2, U: .95}
            if i >= n-2 and month in ['July', 'August']:
                rows.append(zero(sid, month, **{'Store Address Address': fields['Store Address Address']}))
            elif n >= 25 and i == n-3:
                rows.append(zero(sid, month, **{'Store Address Address': fields['Store Address Address'],
                                               'Lifecycle Status': 'closed'}))
            elif n >= 25 and i == n-4 and month == 'August':
                continue
            else:
                if n >= 25 and i == n-5 and month == 'August':
                    fields['% CVR'] = np.nan
                    fields[P] = np.nan
                rows.append(fixture(sid, month, **fields))
    return run(rows, [fixture(month=m, **{G: 500000, N: 200000, D: 30000, T: 40000, P: 3200, C:1000}) for m in months])


def one_opportunity():
    return run([fixture('Priority Central', **{N:10000, '% CVR':0})])


def visual_fixtures():
    return [
        ('One_Store_Healthy', run()),
        ('Four_Opportunities', recommendation_rich(store_count=4)),
        ('Five_Opportunities', recommendation_rich(store_count=5)),
        ('Six_Opportunities', recommendation_rich()),
        ('Zero_Opportunities', no_recommendations()),
        ('Partial_Current_Coverage', current_partial()),
        ('FLOWERS', flowers()),
        ('Eighteen_Stores', large_partner(18)),
        ('Thirty_Stores', large_partner(30)),
    ]
