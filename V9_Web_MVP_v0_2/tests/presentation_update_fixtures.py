"""Presentation QA cases using frozen regression rows and production benchmarks."""
from datetime import date
from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / 'backend' / 'V9_Beta2'
sys.path[:0] = [str(ROOT), str(BACKEND), str(BACKEND / 'tests')]
from analysis import analyze, run_analysis
from config import Settings
from data_pipeline import load_frames, D, N, T, P, C, G, U
from test_regression import fixture, zero


def cases():
    benchmark = pd.read_excel(BACKEND / 'subbusiness_unit_data.xlsx')
    months = ['September', 'October', 'November', 'December', 'January', 'February',
              'March', 'April', 'May', 'June', 'July', 'August']
    rows = []
    for i, month in enumerate(months):
        rows.append(fixture('PETS-01', month, **{
            'Year': 2025 if i < 4 else 2026,
            'Store Name': 'PETS regression partner',
            'Store Address Address': 'Pet Supplies Central, 123 Long Avenue, Tbilisi, Georgia',
            D: 150 + i * 18, N: 1000 + i * 70, T: 400 + i * 20,
            P: 12 + i, C: 3 + i, G: 3000 + i * 190, '% CVR': .12 + i * .006,
            U: .90 + i * .004,
        }))
    def make(sbu, raw):
        return analyze(load_frames(pd.DataFrame(raw), benchmark,
            Settings(partner_sbu=sbu, as_of_date=date(2026, 9, 17))))
    yield 'PETS', make('PETS', rows), 'Synthetic regression partner, 12 months; real PETS benchmark'
    yield 'JEWELRY', run_analysis(Settings()), 'Supplied real partner workbook and JEWELRY benchmark'
    yield 'FLOWERS_partial_missing', make('FLOWERS', [
        fixture('FLOWERS-01', 'June', **{U: .1}),
        fixture('FLOWERS-02', 'June'),
        fixture('FLOWERS-01', **{P: np.nan, U: np.nan,
            'Store Address Address': 'Flowers City Centre, Extended Branch and Collection Point, 123 Chavchavadze Avenue, Tbilisi, Georgia'}),
    ]), 'Regression missing July, current store disappearance, missing PNA/uptime; real FLOWERS benchmark'
    yield 'PETS_zero', make('PETS', [zero('ZERO', 'July'), zero('ZERO')]), 'Regression zero activity; empty eligible Top GMV cohort'
