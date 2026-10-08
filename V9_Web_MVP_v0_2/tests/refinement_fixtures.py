"""Synthetic source rows; every classification and selection uses frozen Beta2."""
from datetime import date
from pathlib import Path
import sys
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
BACKEND=ROOT/'backend/V9_Beta2'
sys.path[:0]=[str(ROOT),str(BACKEND),str(BACKEND/'tests')]
from test_regression import fixture, zero
from config import Settings
from analysis import analyze
from data_pipeline import load_frames,D,N,T,P,C,G,U
from business_classification import classify

LONG_STORE='პეტფუდი — შინაური ცხოველების კვებისა და ვეტერინარული მომსახურების ცენტრი, ჭავჭავაძის გამზირი 123'

def inputs():
    def active(sid,month='August',**kw):
        return fixture(sid,month,**{'Store Address Address':f'Pet supplies branch {sid[-1]}, Rustaveli Avenue 15',
            'Partner Name':'Synthetic Validation Partner','City':'Tbilisi','Country':'Georgia',**kw})
    severe={N:4000,D:100,T:1000,P:450,C:220,G:4000,'% CVR':.025,U:.72}
    for count in (1,2,6):
        rows=[active(f'PRIVATE-ID-{i}',month,**severe) for i in range(count) for month in ['June','July','August']]
        for row in rows:
            if row['Store ID']=='PRIVATE-ID-0':
                row.update({'Store Address Address':LONG_STORE,'City':'თბილისი','Country':'საქართველო'})
        if count==6:
            rows += [active('PRIVATE-AVAIL',**{U:.88,N:30,D:5,T:10,P:0,C:0,G:20,'% CVR':.40})]
            rows += [active('PRIVATE-MISSING',**{P:np.nan})]
            rows += [active('PRIVATE-OLD','June')]
        yield f'Actions_{count}', 'PETS', pd.DataFrame(rows)
    rows=[active('PRIVATE-HYGIENE',month,**{U:.40,N:30,D:5,T:10,P:0,C:0,G:20,'% CVR':.40}) for month in ['June','August']]
    rows += [active('PRIVATE-DATA','June'),active('PRIVATE-DATA',**{P:np.nan})]
    yield 'FLOWERS_missing', 'FLOWERS', pd.DataFrame(rows)
    yield 'Empty', 'PETS', pd.DataFrame([active('PRIVATE-HEALTHY',**{N:1000,D:400,T:410,P:0,C:0,G:8000,U:.98,'% CVR':.40})])

def results():
    benchmarks=pd.read_excel(BACKEND/'subbusiness_unit_data.xlsx')
    for name,sbu,raw in inputs():
        result=analyze(load_frames(raw,benchmarks,Settings(partner_sbu=sbu,as_of_date=date(2026,9,22))))
        yield name,classify(result),raw
