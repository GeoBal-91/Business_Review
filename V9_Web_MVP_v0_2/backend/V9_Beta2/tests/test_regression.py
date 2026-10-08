"""Independent Dev6 decision fixtures; these are NOT the unavailable TC51–TC100."""
import unittest
import json
from pathlib import Path
from datetime import date
from dataclasses import replace
import numpy as np
import pandas as pd
import config as cfg
from config import Settings
from data_pipeline import D,N,T,P,C,G,U,load_frames,DataValidationError
from analysis import analyze
from scoring import interpolate_score,confidence_adjusted_rate,protected_average,_raw_flag
from formatting import format_score


def fixture(sid='A', month='August', **changes):
    r={'Store ID':sid,'Store Address Address':sid,'Month':month,'Year':2026,
       D:200,N:1000,T:400,P:32,C:10,G:2000,U:.95,'% CVR':.2,
       '% PNA Orders':.08,'% Cancels DTP':.025,'Store Sub Business Unit':'PHARMACY_OTC'}
    r.update(changes); return r


def run(rows=None, benchmarks=None, **settings):
    s=Settings(partner_sbu='PHARMACY_OTC',as_of_date=date(2026,9,7),**settings)
    return analyze(load_frames(pd.DataFrame(rows or [fixture()]),pd.DataFrame(benchmarks or [fixture()]),s))


def zero(sid='A',month='August',**kw):
    return fixture(sid,month,**{D:0,N:0,T:0,P:0,C:0,G:0,U:0,'% CVR':0,**kw})


class KeepUnchanged(unittest.TestCase):
    def test_frozen_dev5_constants(self):
        old=json.loads((Path(__file__).parent/'dev5_calibration.json').read_text())
        for key,value in old['constants'].items():
            actual=getattr(cfg,key) if not key.endswith('_WEIGHT') else cfg.WEIGHTS[{'CVR_WEIGHT':'CVR','PNA_WEIGHT':'PNA','CANCELS_WEIGHT':'Cancels','UPTIME_WEIGHT':'Uptime'}[key]]
            with self.subTest(key=key): self.assertEqual(actual,value)
        for key,anchors in old['anchors'].items():
            with self.subTest(key=key): self.assertEqual([list(x) for x in getattr(cfg,key)],anchors)
    def test_all_curve_anchors_midpoints_and_clamps(self):
        old=json.loads((Path(__file__).parent/'dev5_calibration.json').read_text())
        for name,anchors in old['anchors'].items():
            for x,y in anchors: self.assertAlmostEqual(interpolate_score(x,getattr(cfg,name)),y)
            for (x,y),(xx,yy) in zip(anchors,anchors[1:]):
                self.assertAlmostEqual(interpolate_score((x+xx)/2,getattr(cfg,name)),(y+yy)/2)
            self.assertEqual(interpolate_score(-100,getattr(cfg,name)),anchors[0][1])
            self.assertEqual(interpolate_score(10000,getattr(cfg,name)),anchors[-1][1])
    def test_denominator_specific_shrinkage(self):
        a=run([fixture(**{N:150,T:30,D:20,P:9,C:6,'% CVR':.1})])
        m=a.metrics.set_index('metric')
        self.assertAlmostEqual(m.loc['CVR','confidence_weight'],.5)
        self.assertAlmostEqual(m.loc['PNA','confidence_weight'],.5)
        self.assertAlmostEqual(m.loc['Cancels','confidence_weight'],.75)
        self.assertAlmostEqual(m.loc['CVR','adjusted_rate'],.15)
        self.assertAlmostEqual(m.loc['PNA','adjusted_rate'],.19)
        self.assertAlmostEqual(m.loc['Cancels','adjusted_rate'],.15625)
    def test_shrinkage_grid_matches_dev5(self):
        for n in [0,1,10,30,150,10000]:
            for k in [150,30,10]:
                for r,b in [(.01,.2),(.4,.03),(.08,.08)]:
                    self.assertAlmostEqual(confidence_adjusted_rate(r,b,n,k),(n*r+k*b)/(n+k))
    def test_count_first_pna_cancels_aov(self):
        a=run([fixture(),fixture('B',**{D:20,N:100,T:40,P:12,C:8,G:600})])
        r=a.data.monthly.iloc[0]
        self.assertAlmostEqual(r['% PNA Orders'],44/440)
        self.assertAlmostEqual(r['% Cancels DTP'],18/440)
        self.assertAlmostEqual(r['€ AOV Derived'],2600/220)
    def test_dominant_kpi_protection(self):
        self.assertEqual(protected_average([0,0,0,100],[.3,.3,.25,.15]),50)
        self.assertEqual(protected_average([50,50,50,50],[.3,.3,.25,.15]),50)
    def test_zero_delivered_is_active_with_sessions(self):
        a=run([fixture(**{D:0,G:0,N:10000,T:0,P:0,C:0,'% CVR':0})])
        self.assertEqual(a.stores.iloc[0]['Store Status'],'Active')
        self.assertGreater(a.stores.iloc[0]['Opportunity Score'],5)
    def test_zero_delivered_is_active_with_attempts(self):
        a=run([fixture(**{D:0,G:0,N:1000,T:1,P:0,C:1,'% CVR':0})])
        self.assertEqual(a.stores.iloc[0]['Store Status'],'Active')
    def test_two_zero_months_not_closed(self):
        a=run([fixture(month='June'),zero(month='July'),zero()])
        self.assertEqual(a.stores.iloc[0]['Store Status'],'No Activity')
    def test_missing_calendar_month_not_closed(self):
        a=run([fixture(month='April'),zero(month='May'),zero(month='July'),zero()])
        self.assertNotEqual(a.stores.iloc[0]['Store Status'],'Closed')
    def test_reopened_store_active(self):
        a=run([zero(month='May'),zero(month='June'),zero(month='July'),fixture()])
        self.assertEqual(a.stores.iloc[0]['Store Status'],'Active')
    def test_confirmed_closed_and_inactive_zero(self):
        for r in [zero(),zero(**{'Lifecycle Status':'closed'})]:
            a=run([r]); self.assertEqual(a.stores.iloc[0]['Opportunity Score'],0); self.assertFalse(a.actions)
    def test_critical_thresholds_raw_and_separate(self):
        self.assertFalse(_raw_flag('CVR',.06,29,.2))
        self.assertEqual(_raw_flag('CVR',.06,30,.2),'Critical CVR')
        self.assertFalse(_raw_flag('Uptime',.6,None,.95))
        self.assertTrue(_raw_flag('Uptime',.599,None,.95))
        self.assertTrue(_raw_flag('PNA',.3,1,.08)); self.assertTrue(_raw_flag('Cancels',.2,1,.025))
        a=run([fixture(**{D:0,G:0,N:1,T:1,P:0,C:1,'% CVR':0})])
        self.assertIn('Critical Cancels',a.stores.iloc[0]['Critical Flags'])
        self.assertLess(a.stores.iloc[0]['Opportunity Score'],5)
        self.assertTrue(a.reviews)
    def test_short_ranked_list_and_all_actions(self):
        a=run([fixture(str(i),**{N:10000,'% CVR':0}) for i in range(9)])
        self.assertEqual(len(a.opportunities),6); self.assertEqual(len(a.actions),6)
        self.assertEqual([x['Store ID'] for x in a.actions],a.opportunities['Store ID'].tolist())
    def test_flowers_exclusion_and_shared_sbu_calibration(self):
        for sbu in ['FLOWERS','PHARMACY_OTC','PETS','TOYS_GAMES','BOOKS','FASHION','ELECTRONICS','HOME_DECORATION']:
            settings=Settings(partner_sbu=sbu,as_of_date=date(2026,9,7))
            a=analyze(load_frames(pd.DataFrame([fixture()]),pd.DataFrame([fixture(**{'Store Sub Business Unit':sbu})]),settings))
            self.assertAlmostEqual(a.stores.iloc[0]['Opportunity Score'],0)
            self.assertEqual(bool(a.metrics.set_index('metric').loc['Uptime','eligible']),sbu!='FLOWERS')
    def test_honest_top_gmv_title(self):
        self.assertIn("'Top GMV Stores'",(Path(__file__).parents[1]/'slides_stores.py').read_text())


class AuditFixes(unittest.TestCase):
    def test_missing_activity_not_zero(self):
        a=run([fixture(**{D:np.nan,N:np.nan,T:np.nan,P:np.nan,C:np.nan,G:np.nan})])
        self.assertEqual(a.stores.iloc[0]['Store Status'],'Unknown')
        self.assertTrue(pd.isna(a.stores.iloc[0]['Opportunity Score']))
    def test_missing_numerator_incomplete(self):
        a=run([fixture(**{P:np.nan})]); self.assertTrue(pd.isna(a.data.monthly.iloc[0]['% PNA Orders']))
        self.assertEqual(a.stores.iloc[0]['Scoring Status'],'Incomplete')
    def test_invalid_counts_and_dates_rejected(self):
        for changes in [{P:401},{D:-1},{N:float('inf')},{T:3.5},{'Month':'nonsense'}]:
            with self.subTest(changes=changes),self.assertRaises(DataValidationError): run([fixture(**changes)])
    def test_month_formats(self):
        for m in ['Aug','August','8',8]: self.assertEqual(run([fixture(month=m)]).summary['reporting_period'],'2026-08')
    def test_duplicate_grain_rejected(self):
        with self.assertRaises(DataValidationError): run([fixture(),fixture()])
    def test_partition_opt_in_preserves_missing(self):
        a=run([fixture(),fixture(**{P:np.nan})],allow_partitioned_rows=True)
        self.assertEqual(a.data.monthly.iloc[0][D],400)
        self.assertTrue(pd.isna(a.data.monthly.iloc[0][P]))
    def test_reported_cvr_session_weighted(self):
        a=run([fixture(),fixture('B',**{N:100,'% CVR':.8})])
        self.assertAlmostEqual(a.data.monthly.iloc[0]['% CVR'],280/1100)
    def test_explicit_conversion_contracts(self):
        # CHANGE A explicitly retires the two Dev6 alternate scoring contracts.
        for mode in ['converted_sessions','delivered_per_session']:
            with self.assertRaisesRegex(ValueError,'official CVR is reported'):
                run(cvr_mode=mode)
        a=run([fixture(**{'% CVR':.1})])
        self.assertEqual(a.data.monthly.iloc[0]['% CVR'],.1)
        self.assertEqual(a.data.monthly.iloc[0]['Delivered / Sessions Diagnostic'],.2)
    def test_explicit_percentage_units(self):
        a=run([fixture(**{U:'95%','% CVR':'20%'})]); self.assertEqual(a.data.monthly.iloc[0]['% CVR'],.2)
        with self.assertRaises(DataValidationError): run([fixture(**{U:95})])
    def test_activity_closure_conflict_not_hard_zero(self):
        a=run([zero(month='June'),zero(month='July'),fixture(**{U:0})])
        self.assertEqual(a.stores.iloc[0]['Data Quality'],'Conflict')
        self.assertEqual(a.stores.iloc[0]['Store Status'],'Active')
        self.assertTrue(pd.isna(a.stores.iloc[0]['Opportunity Score']))
    def test_inferred_closure_needs_history(self):
        a=run([fixture(month='May'),zero(month='June'),zero(month='July'),zero()])
        self.assertEqual(a.stores.iloc[0]['Closure Evidence'],'Inferred'); self.assertTrue(a.reviews)
        a=run([zero(month='June'),zero(month='July'),zero()])
        self.assertEqual(a.stores.iloc[0]['Store Status'],'No Activity')
    def test_missing_latest_retained(self):
        a=run([fixture('A',month='July'),fixture('B')])
        r=a.stores.set_index('Store ID').loc['A']
        self.assertEqual(r['Store Status'],'Unknown'); self.assertTrue(pd.isna(r[G])); self.assertTrue(pd.isna(r['Opportunity Score']))
    def test_closed_excluded_from_operating_uptime(self):
        a=run([fixture(),zero('B',**{'Lifecycle Status':'closed'})])
        self.assertEqual(a.data.monthly.iloc[0][U],.95)
    def test_missing_cohort_uptime_preserves_assessed_average(self):
        a=run([fixture(),fixture('B',**{U:np.nan})]); self.assertEqual(a.data.monthly.iloc[0][U], .95)
        self.assertEqual(a.data.monthly.iloc[0]['Uptime Value Coverage'],.5)
    def test_flowers_action_follows_eligible_cvr_and_toggle(self):
        for exclude in [True,False]:
            s=Settings(partner_sbu='FLOWERS',flowers_uptime_excluded=exclude,as_of_date=date(2026,9,7))
            a=analyze(load_frames(pd.DataFrame([fixture(**{N:10000,'% CVR':0,U:.4})]),pd.DataFrame([fixture(**{'Store Sub Business Unit':'FLOWERS'})]),s))
            self.assertEqual(a.actions[0]['Metric'],'CVR')
            self.assertEqual(bool(a.metrics.set_index('metric').loc['Uptime','eligible']),not exclude)
            if exclude: self.assertTrue(any(r['Type']=='Opening-hours hygiene' for r in a.reviews))
    def test_exposure_not_added(self):
        a=run([fixture(**{D:0,G:0,N:10000,T:100,P:30,C:100,'% CVR':0})])
        r=a.stores.iloc[0]
        self.assertEqual(r['Modeled Exposure Units'],a.metrics.exposure.max())
        self.assertEqual(r['Main Driver'],'CVR')
    def test_rounding_is_presentation_only(self):
        self.assertEqual(format_score(4.999,5),'<5.00')
        self.assertEqual(format_score(5.001,5),'≥5.00')
        self.assertEqual(format_score(.001),'<0.01')
        a=run([fixture(**{'% CVR':.01})]); value=a.stores.iloc[0]['Opportunity Score']
        self.assertNotEqual(value,round(value,1))
        self.assertTrue(run([fixture(**{'% CVR':.01})],min_priority=value).actions)
        self.assertFalse(run([fixture(**{'% CVR':.01})],min_priority=value+1e-8).actions)
    def test_missing_benchmark_incomplete_no_renormalization(self):
        a=run([fixture(**{U:.4})],[fixture(**{'% CVR':np.nan,P:np.nan,C:np.nan})])
        self.assertEqual(a.stores.iloc[0]['Scoring Status'],'Incomplete')
        self.assertTrue(pd.isna(a.stores.iloc[0]['Performance Severity Score']))
        self.assertEqual(a.stores.iloc[0]['Known Severity'],50)
    def test_stale_benchmark_policy(self):
        a=run(benchmarks=[fixture(month='July')]); self.assertIsNone(a.summary['benchmark_period'])
        a=run(benchmarks=[fixture(month='July')],max_benchmark_lag_months=1)
        self.assertEqual(a.summary['benchmark_period'],'2026-07')
    def test_current_month_requires_opt_in(self):
        with self.assertRaises(DataValidationError): run([fixture(month='September')],[fixture(month='September')])
    def test_history_baseline_restoration_monotonic(self):
        values=[]
        for u,n in [(.5,500),(.1,100),(.01,10)]:
            rows=[fixture(month='June',**{T:1000}),fixture(month='July',**{T:1000}),fixture(**{U:u,T:n,D:0,G:0,P:0,C:0})]
            a=run(rows); m=a.metrics.set_index('metric').loc['Uptime']
            self.assertIn('Healthy-month baseline',m.exposure_basis); values.append(m.exposure)
        self.assertEqual(values,sorted(values)); self.assertGreater(values[-1],values[0])
    def test_row_order_and_gmv_invariance(self):
        rows=[fixture('B',**{'% CVR':.01}),fixture('A',**{'% CVR':.01})]
        a,b=run(rows),run(rows[::-1])
        self.assertEqual(a.opportunities['Store ID'].tolist(),b.opportunities['Store ID'].tolist())
        c=run([{**r,G:r[G]*100} for r in rows])
        self.assertEqual(a.stores['Opportunity Score'].tolist(),c.stores['Opportunity Score'].tolist())
    def test_partner_average_cannot_mask_store_action(self):
        a=run([fixture('Bad',**{N:10000,'% CVR':0}),fixture('Good',**{N:1000000,'% CVR':.8})])
        self.assertGreater(a.data.monthly.iloc[0]['% CVR'],.2)
        self.assertIn('Bad',[x['Store ID'] for x in a.actions])
    def test_commercial_status_independent_of_uptime(self):
        a=run([fixture('A',**{G:500,U:.4}),fixture('B',**{G:5000})])
        self.assertEqual(a.stores.set_index('Store ID').loc['A','Commercial Status'],'Growth Potential')
    def test_challenger_and_paired_both_zero_floor(self):
        for model in ['paired','simple_product']:
            a=run([fixture(**{D:0,G:0,N:1,T:1,P:0,C:1,'% CVR':0})],priority_model=model)
            self.assertLess(a.stores.iloc[0]['Opportunity Score'],5)
    def test_december_january_consecutive(self):
        rows=[fixture(month='October',Year=2025),zero(month='November',Year=2025),zero(month='December',Year=2025),zero(month='January')]
        a=run(rows,[fixture(month='January')]); self.assertEqual(a.stores.iloc[0]['Store Status'],'Closed')


if __name__=='__main__': unittest.main()
