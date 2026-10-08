"""Dev6.1.2: presentation guards, valid-current GMV selection and action UX."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from dataclasses import replace
import numpy as np
import pandas as pd
from test_regression import fixture, run
from test_presentation_patch import blank, full_deck, slide_text
from test_hardening import text_of
from presentation_hardening_fixtures import recommendation_rich, no_recommendations, current_partial, historical_gap
from presentation_hardening import benchmark_display, top_gmv_rows, action_focus, build_recommendations, COVERAGE_BENCHMARK_NOTE
from presentation_polish import top_gmv_concentration
from data_pipeline import G, N, D, T
from formatting import benchmark_gap_info, format_score, format_percent, format_currency_2


class AggregateCoverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.partial = current_partial(); cls.partial_deck = full_deck(cls.partial)
        cls.complete = run(); cls.complete_deck = full_deck(cls.complete)
        cls.history = historical_gap(); cls.history_deck = full_deck(cls.history)

    def test_partial_all_current_benchmark_slides_suppress_direction(self):
        for title in ['Executive Summary', 'Partner vs PHARMACY_OTC', 'Operational Health']:
            text = slide_text(self.partial_deck, title)
            self.assertIn(COVERAGE_BENCHMARK_NOTE, text)
            self.assertNotRegex(text.lower(), r'\b(better|worse|above|below)\b|in line with')
            self.assertIn('Expected 2 · Present 1 · Missing 1', text)

    def test_partial_partner_table_all_five_raw_pairs_retained(self):
        text = slide_text(self.partial_deck, 'Partner vs PHARMACY_OTC')
        self.assertEqual(text.count(COVERAGE_BENCHMARK_NOTE), 6)  # five rows + takeaway
        for word in ['AOV','CVR','Uptime','PNA','Cancels','€10.00','20.0%','95.0%','16.0%','8.0%','5.0%','2.5%']:
            self.assertIn(word, text)
        self.assertNotIn('Comparable period:', text)

    def test_partial_executive_keeps_raw_current_and_sbu_values(self):
        text = slide_text(self.partial_deck, 'Executive Summary')
        for word in ['GMV\n€1,000','Orders\n100','AOV\n€10.00','Partner CVR\n20.0%',
                     'SBU AOV: €10.00','SBU CVR: 20.0%','Partner vs SBU AOV: '+COVERAGE_BENCHMARK_NOTE,
                     'Partner vs SBU CVR: '+COVERAGE_BENCHMARK_NOTE,'MoM: Not comparable']:
            self.assertIn(word, text)

    def test_partial_operational_keeps_raw_rates_and_references(self):
        text = slide_text(self.partial_deck, 'Operational Health')
        for word in ['Operating Store Uptime\n95.0%','Partner PNA\n16.0%','Partner Cancels\n5.0%',
                     'Target: 95.0%','SBU PNA: 8.0%','SBU Cancels: 2.5%','MoM: Not comparable']:
            self.assertIn(word, text)

    def test_complete_comparisons_keep_normal_interpretation(self):
        for title in ['Executive Summary','Partner vs PHARMACY_OTC','Operational Health']:
            text=slide_text(self.complete_deck,title)
            self.assertNotIn(COVERAGE_BENCHMARK_NOTE,text)
            self.assertIn('In line with',text)

    def test_historical_gap_does_not_suppress_complete_current(self):
        for title in ['Executive Summary','Partner vs PHARMACY_OTC','Operational Health']:
            text=slide_text(self.history_deck,title)
            self.assertNotIn(COVERAGE_BENCHMARK_NOTE,text)
            self.assertIn('In line with',text)
        self.assertIn('MoM: Not comparable',slide_text(self.history_deck,'Executive Summary'))

    def test_display_guard_preserves_all_complete_formatter_branches(self):
        for metric, reference in [('pp',.2),('relative',10)]:
            for value in [None,0,reference*.5,reference,reference*2]:
                for higher in [True,False]:
                    expected=benchmark_gap_info(value,reference,metric_type=metric,higher_is_better=higher)
                    self.assertEqual(benchmark_display(value,reference,False,metric_type=metric,higher_is_better=higher),expected)
                    self.assertEqual(benchmark_display(value,reference,True)['text'],COVERAGE_BENCHMARK_NOTE)

    def test_guard_does_not_hide_separate_store_diagnostics(self):
        text=text_of(self.partial_deck)
        self.assertIn('Store Diagnostics',text)
        self.assertIn('UNKNOWN',text)
        self.assertIn('Operational & Data Review',text)
        self.assertIn('Large',text)


class TopGMVEligibility(unittest.TestCase):
    def test_one_current_plus_one_missing_store(self):
        a=current_partial(); shown=top_gmv_rows(a)
        self.assertEqual(shown['Store ID'].tolist(),['Small'])
        text=slide_text(full_deck(a),'Top GMV Stores')
        self.assertNotIn('Large',text);self.assertIn('1 store displayed',text)
        self.assertIn('GMV share not assessed — incomplete store coverage.',text)
        self.assertEqual(len(a.stores),2)

    def test_fewer_than_six_valid_rows_and_share(self):
        for n in [1,2,5]:
            a=run([fixture(str(i)) for i in range(n)])
            shown=top_gmv_rows(a)
            self.assertEqual(len(shown),n)
            self.assertEqual(top_gmv_concentration(a,shown),(n,1.,''))

    def test_missing_current_gmv_not_zero_imputed(self):
        a=run([fixture('Missing',**{G:np.nan}),fixture('Valid')])
        self.assertEqual(top_gmv_rows(a)['Store ID'].tolist(),['Valid'])
        self.assertTrue(pd.isna(a.stores.set_index('Store ID').loc['Missing',G]))

    def test_infinite_values_excluded_at_presentation_boundary(self):
        a=run([fixture('A'),fixture('B'),fixture('C')])
        a.stores[G] = a.stores[G].astype(float)
        a.stores.loc[a.stores['Store ID']=='A',G]=np.inf
        a.stores.loc[a.stores['Store ID']=='B',G]=-np.inf
        self.assertEqual(top_gmv_rows(a)['Store ID'].tolist(),['C'])

    def test_observed_zero_gmv_excluded(self):
        a=run([fixture('Zero',**{G:0}),fixture('Positive')])
        self.assertEqual(top_gmv_rows(a)['Store ID'].tolist(),['Positive'])
        self.assertGreater(top_gmv_rows(a).iloc[-1][G],0)

    def test_noncurrent_or_unobserved_records_excluded(self):
        a=run([fixture('A'),fixture('B'),fixture('C')])
        a.stores.loc[a.stores['Store ID']=='A','Period']=pd.Timestamp('2026-07-01')
        a.stores.loc[a.stores['Store ID']=='B','Last Observed Period']=pd.Timestamp('2026-07-01')
        self.assertEqual(top_gmv_rows(a)['Store ID'].tolist(),['C'])

    def test_unknown_current_status_not_ranked(self):
        a=run([fixture('Unknown',**{D:np.nan,N:np.nan,T:np.nan}),fixture('Known')])
        self.assertEqual(a.stores.set_index('Store ID').loc['Unknown','Store Status'],'Unknown')
        self.assertEqual(top_gmv_rows(a)['Store ID'].tolist(),['Known'])

    def test_valid_order_deterministic_and_capped_at_six(self):
        rows=[fixture(sid,**{G:2000 if sid<'E' else 1000}) for sid in list('HGFEDCBA')]
        a,b=run(rows),run(rows[::-1])
        before=a.stores.copy(deep=True)
        self.assertEqual(top_gmv_rows(a)['Store ID'].tolist(),list('ABCDEF'))
        self.assertEqual(top_gmv_rows(a)['Store ID'].tolist(),top_gmv_rows(b)['Store ID'].tolist())
        pd.testing.assert_frame_equal(a.stores,before,check_exact=True)

    def test_no_valid_current_rows_has_explicit_empty_display(self):
        a=run([fixture(**{G:np.nan})])
        self.assertTrue(top_gmv_rows(a).empty)
        text=slide_text(full_deck(a),'Top GMV Stores')
        self.assertIn('No positive-GMV stores available for the current period.',text)
        self.assertIn('0 stores displayed',text)


class RecommendationsUX(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rich=recommendation_rich()
        cls.prs=blank();build_recommendations(cls.prs,cls.rich)

    def test_ranked_business_content_preserved_in_order(self):
        text=text_of(self.prs);positions=[]
        self.assertGreaterEqual(len(self.rich.actions),3)
        for a in self.rich.actions:
            header=f"{a['Store']} · {a['Metric']} · Priority {format_score(a['Priority'],self.rich.settings.min_priority)}"
            positions.append(text.index(header))
            for field in ['Issue','Action','Intended Effect']:self.assertIn(a[field],text)
        self.assertEqual(positions,sorted(positions))
        self.assertEqual(len(self.prs.slides),(len(self.rich.actions)+2)//3)

    def test_focus_uses_highest_ranked_displayed_kpi_and_actual_range(self):
        for start in range(0,len(self.rich.actions),3):
            shown=self.rich.actions[start:start+3];focus=action_focus(self.rich,shown)
            self.assertEqual(focus['primary_kpi'],shown[0]['Metric'])
            self.assertEqual(focus['store_count'],len({a['Store ID'] for a in shown}))
            self.assertEqual(focus['highest_priority'],max(a['Priority'] for a in shown))
            self.assertEqual(focus['lowest_priority'],min(a['Priority'] for a in shown))

    def test_review_count_is_separate_and_limited_to_displayed_stores(self):
        shown=self.rich.actions[:3];ids={a['Store ID'] for a in shown}
        enriched=replace(self.rich,reviews=self.rich.reviews+[{'Store ID':'Unrelated'}])
        focus=action_focus(enriched,shown)
        self.assertEqual(focus['review_count'],sum(r['Store ID'] in ids for r in self.rich.reviews))
        self.assertIn('Separate from business Priority',text_of(self.prs))

    def test_empty_recommendations_has_no_fake_focus_metrics(self):
        a=no_recommendations();self.assertEqual(a.actions,[])
        prs=blank();build_recommendations(prs,a);text=text_of(prs)
        self.assertEqual(len(prs.slides),1);self.assertIsNone(action_focus(a,[]))
        self.assertIn('No material business opportunities',text)
        self.assertIn('Review operational/data observations separately.',text)
        for label in ['Primary KPI','Stores requiring action','Priority range','Critical / review items']:
            self.assertNotIn(label,text)

    def test_execution_reminder_present_without_forecasts_or_dates(self):
        text=text_of(self.prs)
        for t in ['Confirm priority stores','Assign owner / deadline','Track progress next review']:
            self.assertIn(t,text)
        self.assertNotRegex(text.lower(),r'expected gmv|expected order uplift|financial recovery|implementation date')

    def test_focus_one_store_and_duplicate_records_uses_distinct_ids(self):
        a=self.rich.actions[0]
        focus=action_focus(self.rich,[a,a])
        self.assertEqual(focus['store_count'],1)
        self.assertEqual(focus['highest_priority'],focus['lowest_priority'])

    def test_rendering_does_not_mutate_actions_reviews_or_full_precision(self):
        before=json.dumps({'actions':self.rich.actions,'reviews':self.rich.reviews},sort_keys=True)
        prs=blank();build_recommendations(prs,self.rich)
        self.assertEqual(before,json.dumps({'actions':self.rich.actions,'reviews':self.rich.reviews},sort_keys=True))


class FrozenAnalyticalRelease(unittest.TestCase):
    def test_analytical_files_and_all_98_test_definitions_byte_identical(self):
        root=Path(__file__).parents[1]
        baseline=json.loads((root/'tests/dev6_1_1_frozen_baseline.json').read_text())
        for name,digest in baseline['frozen_files'].items():
            self.assertEqual(hashlib.sha256((root/name).read_bytes()).hexdigest(),digest,name)

    def test_all_bundled_analytical_exports_byte_identical(self):
        from main import export_analysis
        from analysis import run_analysis
        from config import Settings
        root=Path(__file__).parents[1]
        baseline=json.loads((root/'tests/dev6_1_1_frozen_baseline.json').read_text())
        a=run_analysis(Settings(input_file=str(root/'partner_data.xlsx'),subbusiness_file=str(root/'tests/beta1_1_benchmark_reference.xlsx')))
        with tempfile.TemporaryDirectory() as tmp:
            export_analysis(a,Path(tmp))
            for name,digest in baseline['analytical_exports'].items():
                self.assertEqual(hashlib.sha256((Path(tmp)/name).read_bytes()).hexdigest(),digest,name)
