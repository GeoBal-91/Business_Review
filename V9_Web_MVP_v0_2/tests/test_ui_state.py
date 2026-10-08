"""Regression checks for review inputs and validation reuse."""
from io import BytesIO
from pathlib import Path
from unittest.mock import patch
import sys
import unittest
from PIL import Image
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from web.services import invoke


def logo(color):
    out = BytesIO()
    Image.new('RGB', (60,30), color).save(out, 'PNG')
    return out.getvalue()


class UIState(unittest.TestCase):
    def test_logo_reuses_validation_and_reset_clears_sbu(self):
        with patch('web.services.invoke', wraps=invoke) as bridge:
            app = AppTest.from_file(str(ROOT/'app.py'), default_timeout=120).run()
            app.text_input[0].set_value('PetFood')
            app.file_uploader[0].set_value(('partner.xlsx', (ROOT/'backend/V9_Beta2/partner_data.xlsx').read_bytes(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))
            app.selectbox[0].select('JEWELRY').run()
            count = lambda: sum(c.args[0] == 'validate' for c in bridge.call_args_list)
            self.assertEqual(count(), 1)
            app.file_uploader[1].set_value(('logo.png', logo('red'), 'image/png')).run()
            app.file_uploader[1].set_value(('logo.png', logo('blue'), 'image/png')).run()
            self.assertEqual(count(), 1)
            self.assertFalse(app.exception)
            self.assertFalse(next(b for b in app.button if b.label=='Generate Review').disabled)
            app.file_uploader[1].set_value(('bad.png', b'not a valid image', 'image/png')).run()
            self.assertTrue(next(b for b in app.button if b.label=='Generate Review').disabled)
            self.assertTrue(app.error)
            self.assertEqual(count(), 1)
            app.selectbox[0].select('ICE_CREAM').run()
            self.assertEqual(count(), 2)
            self.assertTrue(next(b for b in app.button if b.label=='Generate Review').disabled)
            next(b for b in app.button if b.label=='Clear uploads and results').click().run()
            self.assertIsNone(app.selectbox[0].value)
            self.assertEqual(app.text_input[0].value, '')
            self.assertIsNone(app.file_uploader[0].value)
            self.assertIsNone(app.file_uploader[1].value)
            self.assertFalse(app.exception)
