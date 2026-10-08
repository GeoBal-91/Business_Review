"""Reproducible state-aware dashboard and coverage/model visual fixtures."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
from pptx import Presentation
from pptx.util import Inches
from test_regression import fixture,zero,run
from test_hardening import disappearance
from data_pipeline import D,N,T,P,C,G,U
from diagnostics import build
from presentation import render


def build_examples(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    cases=[
        run([fixture('Healthy',**{'Store Name':'Healthy store','City':'Tbilisi'})]),
        run([fixture('Material',**{N:10000,'% CVR':0})]),
        run([fixture('Incomplete',**{N:10000,'% CVR':0,P:float('nan')})]),
        run([zero('Confirmed closed',**{'Lifecycle Status':'closed'})]),
        run([fixture('No activity','July'),zero('No activity')]),
        run([fixture('Small critical observation',**{D:0,G:0,N:1,T:5,P:0,C:1,'% CVR':0})]),
        run([fixture('Main action differs from worst KPI',**{D:0,G:0,N:100000,T:1,P:0,C:1,'% CVR':.18})]),
        run([fixture('Main action differs from largest exposure',**{D:0,G:0,N:100000,T:500,P:0,C:250,'% CVR':.18})]),
        run([fixture('Trend with missing months','March',**{'% CVR':.15}),fixture('Trend with missing months','May',**{'% CVR':.10}),fixture('Trend with missing months',**{'% CVR':.05})]),
        run([fixture('All critical',**{N:10000,T:1000,D:0,G:0,P:600,C:900,U:.1,'% CVR':0})]),
        run([fixture('Missing current store','July'),fixture('Present store')]),
    ]
    prs=Presentation();prs.slide_width=Inches(13.333);prs.slide_height=Inches(7.5)
    charts=output/'charts';charts.mkdir(exist_ok=True)
    for a in cases: build(prs,a,lambda name:str(charts/name))
    prs.save(output/'dashboard_states.pptx')
    render(disappearance(),output/'partial_store_coverage.pptx')
    a=run([fixture(month='September')],[fixture(month='September')],allow_partial_period=True,priority_model='simple_product')
    render(a,output/'provisional_challenger.pptx')

if __name__=='__main__': build_examples(sys.argv[1])
