from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from zipfile import ZipFile
import pandas as pd
from PIL import Image
from pptx import Presentation

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from web.services import BACKEND, WebError, baseline_fingerprint, invoke, normalize_logo
from web.services import input_key
from web.version import PRESENTATION_VERSION


def workbook(frame):
    stream = BytesIO()
    frame.to_excel(stream, index=False)
    return stream.getvalue()


def logo(color):
    stream = BytesIO()
    Image.new('RGB', (120, 60), color).save(stream, 'PNG')
    return stream.getvalue()


class WebSmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.partner = (BACKEND / 'partner_data.xlsx').read_bytes()
        cls.frame = pd.read_excel(BytesIO(cls.partner))
        cls.logo = logo('purple')

    def test_catalog(self):
        result = invoke('catalog')
        self.assertEqual(len(result['sbus']), 43)
        self.assertIn('PHARMACY_RX', result['sbus'])
        self.assertEqual(result['sbus'], sorted(set(result['sbus'])))

    def test_presentation_version_invalidates_cached_result(self):
        key = input_key(b'partner', b'logo', 'PETS', 'baseline')
        self.assertTrue(PRESENTATION_VERSION)
        self.assertNotEqual(key, input_key(b'partner', b'logo', 'PETS', 'other-baseline'))

    def test_valid_metadata(self):
        result = invoke('validate', self.partner, sbu='JEWELRY')
        self.assertTrue(result['ok'], result)
        self.assertEqual(result['metadata']['period'], 'August 2026')
        self.assertEqual(result['metadata']['store_count'], 1)
        self.assertEqual(result['metadata']['partner'], 'Not included in export')
        f = self.frame.assign(**{'Partner Name': 'Example Partner'})
        self.assertEqual(invoke('validate', workbook(f), sbu='JEWELRY')['metadata']['partner'], 'Example Partner')

    def test_blocking_validation(self):
        cases = []
        cases.append(('schema', self.frame.drop(columns=['% CVR']), 'JEWELRY', 'missing_columns'))
        cases.append(('duplicates', pd.concat([self.frame, self.frame]), 'JEWELRY', 'duplicate_grain'))
        bad = self.frame.copy(); bad.loc[0, '% CVR'] = 3
        cases.append(('rate', bad, 'JEWELRY', 'invalid_rate'))
        bad = self.frame.copy(); bad.loc[0, 'Sessions Store'] = -1
        cases.append(('count', bad, 'JEWELRY', 'invalid_number'))
        bad = self.frame.copy(); bad.loc[0, 'Month'] = 'Oops'
        cases.append(('period', bad, 'JEWELRY', 'invalid_period'))
        bad = self.frame.copy(); bad['Year'] = 2027
        cases.append(('partial', bad, 'JEWELRY', 'partial_period'))
        cases.append(('unknown SBU', self.frame, 'NOT_REAL', 'empty_input'))
        cases.append(('missing CVR', self.frame, 'ICE_CREAM', 'web_benchmark_incomplete'))
        bad = self.frame.copy(); bad['Year'] = 2024
        cases.append(('benchmark date', bad, 'JEWELRY', 'future_benchmarks'))
        bad = self.frame.copy(); bad['Partner Name'] = ['A'] + ['B'] * (len(bad)-1)
        cases.append(('multiple partners', bad, 'JEWELRY', 'web_multiple_partners'))
        for name, frame, sbu, code in cases:
            with self.subTest(name=name):
                result = invoke('validate', workbook(frame), sbu=sbu)
                self.assertFalse(result['ok'])
                self.assertIn(code, [i['code'] for i in result['issues']])

    def test_upload_boundaries(self):
        for content in (b'', b'not excel', b'x' * (20*1024*1024+1)):
            with self.assertRaises(WebError):
                invoke('validate', content, sbu='JEWELRY')
        for content in (b'', b'not image', b'x' * (5*1024*1024+1)):
            with self.assertRaises(WebError):
                normalize_logo(content)

    def test_cleanup_failure_and_timeout(self):
        with TemporaryDirectory() as tmp:
            self.assertFalse(invoke('validate', workbook(self.frame.drop(columns=['% CVR'])), sbu='JEWELRY', temp_parent=tmp)['ok'])
            self.assertEqual(list(Path(tmp).iterdir()), [])
            with self.assertRaises(WebError):
                invoke('validate', self.partner, sbu='JEWELRY', timeout=.001, temp_parent=tmp)
            self.assertEqual(list(Path(tmp).iterdir()), [])
            with patch('web.services.subprocess.run', side_effect=OSError('failure')):
                with self.assertRaises(WebError):
                    invoke('validate', self.partner, sbu='JEWELRY', temp_parent=tmp)
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_generate_parity_isolation_and_cleanup(self):
        before = baseline_fingerprint()
        with TemporaryDirectory() as tmp:
            with ThreadPoolExecutor(max_workers=2) as pool:
                futures = [pool.submit(invoke, 'generate', self.partner, logo(c), 'JEWELRY', partner_name='PetFood', temp_parent=tmp) for c in ('red', 'blue')]
                results = [f.result() for f in futures]
            self.assertEqual(list(Path(tmp).iterdir()), [])
            for result, color in zip(results, ('red', 'blue')):
                self.assertTrue(result['ok'], result)
                deck = Presentation(BytesIO(result['pptx']))
                self.assertGreater(len(deck.slides), 15)
                expected = hashlib.sha256(normalize_logo(logo(color))).hexdigest()
                with ZipFile(BytesIO(result['pptx'])) as z:
                    self.assertIn(expected, [hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('ppt/media/')])
                with ZipFile(BytesIO(result['audit'])) as z:
                    self.assertIsNone(z.testzip())
                    self.assertEqual(json.loads(z.read('web_run.json'))['logo_sha256'], expected)
                    self.assertIn('Classification_Rule_Trace.json', z.namelist())
            # Compare all numerical/classification CSV outputs to the untouched CLI.
            target = Path(tmp) / 'direct.pptx'
            run = subprocess.run([sys.executable, str(BACKEND/'main_v2_1.py'), '--partner', str(BACKEND/'partner_data.xlsx'),
                                  '--sbu', 'JEWELRY', '--output', str(target), '--analysis-only'],
                                  cwd=tmp, capture_output=True, timeout=120, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
            self.assertEqual(run.returncode, 0, run.stderr.decode())
            with ZipFile(BytesIO(results[0]['audit'])) as z:
                for path in target.with_name('direct_audit').glob('*.csv'):
                    self.assertEqual(z.read(path.name), path.read_bytes(), path.name)
            # Optional private artifact for visual QA; never required by the test.
            if os.environ.get('V9_SMOKE_ARTIFACT_DIR'):
                out = Path(os.environ['V9_SMOKE_ARTIFACT_DIR']); out.mkdir(parents=True, exist_ok=True)
                (out/'smoke.pptx').write_bytes(results[0]['pptx'])
        self.assertEqual(before, baseline_fingerprint())

    def test_streamlit_flow(self):
        from streamlit.testing.v1 import AppTest
        at = AppTest.from_file(str(ROOT/'app.py'), default_timeout=180).run()
        button = lambda label: next(b for b in at.button if b.label == label)
        self.assertFalse(at.exception)
        self.assertTrue(button('Generate Review').disabled)
        at.file_uploader[0].set_value(('partner.xlsx', self.partner, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))
        at.selectbox[0].select('JEWELRY').run()
        self.assertTrue(button('Generate Review').disabled)  # Logo required.
        at.file_uploader[1].set_value(('logo.png', self.logo, 'image/png')).run()
        self.assertTrue(button('Generate Review').disabled)
        at.text_input[0].set_value('PetFood').run()
        self.assertFalse(at.exception)
        self.assertFalse(button('Generate Review').disabled)
        button('Generate Review').click().run()
        self.assertFalse(at.exception)
        self.assertEqual(len(at.download_button), 2)
        at.selectbox[0].select('ICE_CREAM').run()
        self.assertTrue(button('Generate Review').disabled)
        self.assertEqual(len(at.download_button), 0)
        self.assertTrue(at.error)
        button('Clear uploads and results').click().run()
        self.assertIsNone(at.file_uploader[0].value)
        self.assertIsNone(at.file_uploader[1].value)
        self.assertTrue(button('Generate Review').disabled)


if __name__ == '__main__':
    unittest.main()
