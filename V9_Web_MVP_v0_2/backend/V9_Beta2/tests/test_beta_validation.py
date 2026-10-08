"""Validation exports preserve engine values and leave every AM judgment empty."""
import ast
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import pandas as pd
from pandas.testing import assert_frame_equal
from beta_validation import store_frame, partner_frame, export_validation, validation_schema, STORE_MANUAL_COLUMNS, PARTNER_MANUAL_COLUMNS
from beta_fixtures import large_partner, flowers
from presentation_hardening_fixtures import current_partial, recommendation_rich
from test_regression import run, fixture
from main import export_analysis, main
from analysis import run_analysis
from config import Settings
from data_pipeline import G, D, N, T, U


class ValidationStores(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a=large_partner(30);cls.frame=store_frame(cls.a)

    def test_every_known_store_retained_once_no_duplicate_name_merging(self):
        a=run([fixture('ID-A',**{'Store Address Address':'Same address'}),fixture('ID-B',**{'Store Address Address':'Same address'})])
        self.assertEqual(store_frame(a)['Store ID'].tolist(),a.stores['Store ID'].tolist())
        self.assertEqual(len(self.frame),len(self.a.stores))
        self.assertEqual(self.frame['Store ID'].tolist(),self.a.stores['Store ID'].tolist())

    def test_minimum_columns_and_full_precision_scores_match(self):
        source=self.a.stores.set_index('Store ID');actual=self.frame.set_index('Store ID')
        fields={'GMV':G,'Delivered Orders':D,'Sessions':N,'Order Attempts':T,'CVR':'% CVR',
                'PNA':'% PNA Orders','Cancels':'% Cancels DTP','Uptime':U,'Severity':'Performance Severity Score',
                'Impact':'Business Impact Score','Priority':'Opportunity Score','Main Action KPI':'Main Driver',
                'Eligible Opportunity':'Eligible Opportunity','Critical Flags':'Critical Flags','Scoring Status':'Scoring Status',
                'Operational Status':'Operational Status','Store Status':'Store Status','AOV':'€ AOV Derived',
                'Severity Driver':'Severity Driver','Impact Source':'Impact Source'}
        for label,key in fields.items():
            pd.testing.assert_series_equal(actual[label],source[key],check_names=False,check_exact=True)

    def test_reported_official_cvr_not_delivered_proxy(self):
        a=run([fixture(**{'% CVR':.12345678901234567})]);row=store_frame(a).iloc[0]
        self.assertEqual(row['CVR'],a.stores.iloc[0]['% CVR']);self.assertNotEqual(row['CVR'],row['Delivered Orders']/row['Sessions'])

    def test_missing_current_and_incomplete_values_stay_blank_not_zero(self):
        a=current_partial();frame=store_frame(a).set_index('Store ID')
        for label in ['GMV','CVR','Priority','Severity','Impact']:
            self.assertTrue(pd.isna(frame.loc['Large',label]))
        with tempfile.TemporaryDirectory() as tmp:
            export_validation(a,tmp)
            reloaded=pd.read_csv(Path(tmp)/'Beta_Validation_Stores.csv',keep_default_na=False)
            row=reloaded.set_index('Store ID').loc['Large']
            for label in ['GMV','CVR','Priority','Severity','Impact']:self.assertEqual(row[label],'')

    def test_selected_ranks_actions_and_evidence_exact_lineage(self):
        actual=self.frame.set_index('Store ID');rank=self.a.opportunities.set_index('Store ID')['Rank']
        for action in self.a.actions:
            row=actual.loc[action['Store ID']]
            self.assertEqual(row['Opportunity Rank'],rank.loc[action['Store ID']])
            self.assertEqual(row['Recommended Action'],action['Action'])
            self.assertEqual(row['Evidence'],action['Issue'])
            self.assertEqual(row['Intended Effect'],action['Intended Effect'])
            self.assertEqual(row['Priority'],action['Priority'])

    def test_unselected_eligible_keeps_eligibility_but_no_invented_rank(self):
        a=run([fixture(str(i),**{N:10000,'% CVR':0}) for i in range(9)])
        frame=store_frame(a)
        self.assertEqual(int(frame['Eligible Opportunity'].sum()),9)
        self.assertEqual(int(frame['Displayed Opportunity'].sum()),6)
        self.assertEqual(int(frame['Opportunity Rank'].notna().sum()),6)

    def test_all_store_manual_columns_empty(self):
        self.assertTrue((self.frame[STORE_MANUAL_COLUMNS]=='').all().all())

    def test_partner_identity_blank_and_all_am_fields_empty(self):
        row=partner_frame(self.a).iloc[0]
        self.assertEqual(row['Partner / Identifier'],'')
        self.assertEqual(row['Reporting Period'],self.a.summary['reporting_period'])
        self.assertEqual(row['SBU'],self.a.settings.partner_sbu)
        self.assertTrue(all(row[name]=='' for name in PARTNER_MANUAL_COLUMNS))

    def test_expected_values_documented_without_populating_judgments(self):
        schema=validation_schema()
        self.assertEqual(set(schema['store_manual_expected_values']),set(STORE_MANUAL_COLUMNS))
        self.assertEqual(set(schema['partner_manual_expected_values']),set(PARTNER_MANUAL_COLUMNS))
        self.assertEqual(schema['store_manual_expected_values']['AM_Should_Be_Priority'],'Yes / Partly / No')
        self.assertIn('not percentages',schema['missing_values'])

    def test_csv_round_trip_full_precision_and_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            export_analysis(self.a,tmp)
            frame=pd.read_csv(Path(tmp)/'Beta_Validation_Stores.csv',float_precision='round_trip')
            for key in ['Priority','Severity','Impact','CVR','PNA','Cancels','Uptime']:
                pd.testing.assert_series_equal(frame[key],self.frame[key],check_exact=True)
            for name in ['stores.csv','metrics.csv','opportunities.csv','actions.csv','reviews.csv',
                         'run_audit.json','metric_records.json','Beta_Validation_Partner.csv','Beta_Validation_Schema.json']:
                self.assertTrue((Path(tmp)/name).is_file())

    def test_analysis_only_cli_emits_validation_files(self):
        with tempfile.TemporaryDirectory() as tmp, patch('main.run_analysis',return_value=run()):
            path=Path(tmp)/'Beta.pptx'
            main(['--analysis-only','--output',str(path)])
            self.assertFalse(path.exists())
            self.assertTrue((Path(tmp)/'Beta_audit/Beta_Validation_Stores.csv').is_file())
            self.assertTrue((Path(tmp)/'Beta_audit/Beta_Validation_Partner.csv').is_file())

    def test_export_read_only_and_challenger_still_available(self):
        a=flowers();frames={k:getattr(a,k).copy(deep=True) for k in ['stores','metrics','opportunities']}
        other=json.dumps([a.actions,a.reviews,a.summary],default=str,sort_keys=True)
        with tempfile.TemporaryDirectory() as tmp:export_analysis(a,tmp)
        for key,before in frames.items():assert_frame_equal(before,getattr(a,key),check_exact=True)
        self.assertEqual(other,json.dumps([a.actions,a.reviews,a.summary],default=str,sort_keys=True))
        self.assertIn('Simple Product Priority',store_frame(a))


class FrozenDev612(unittest.TestCase):
    def test_engine_config_dependencies_assets_and_analytical_fixtures_byte_identical(self):
        root=Path(__file__).parents[1]
        baseline=json.loads((root/'tests/beta_baseline.json').read_text())
        for name,digest in baseline['frozen_files'].items():
            self.assertEqual(hashlib.sha256((root/name).read_bytes()).hexdigest(),digest,name)

    def test_existing_analytical_test_functions_unedited(self):
        root=Path(__file__).parents[1]
        baseline=json.loads((root/'tests/beta_baseline.json').read_text())
        for name,functions in baseline['unchanged_test_functions'].items():
            tree=ast.parse((root/name).read_text())
            actual={node.name:hashlib.sha256(ast.dump(node).encode()).hexdigest()
                    for node in ast.walk(tree) if isinstance(node,ast.FunctionDef)}
            for name,digest in functions.items():self.assertEqual(actual[name],digest,name)

    def test_same_uploaded_inputs_all_analytical_csv_and_metric_json_bytes_identical(self):
        root=Path(__file__).parents[1]
        baseline=json.loads((root/'tests/beta_baseline.json').read_text())
        a=run_analysis(Settings(subbusiness_file=root/'tests/beta1_1_benchmark_reference.xlsx'))
        with tempfile.TemporaryDirectory() as tmp:
            export_analysis(a,tmp)
            for name,digest in baseline['uploaded_analytical_exports'].items():
                self.assertEqual(hashlib.sha256((Path(tmp)/name).read_bytes()).hexdigest(),digest,name)
