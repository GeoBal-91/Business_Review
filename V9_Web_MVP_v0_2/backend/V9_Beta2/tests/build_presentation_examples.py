"""Reproduce the presentation-patch UX examples from explicit synthetic fixtures."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from pptx import Presentation
from ppt_core import add_text
from presentation import render
from main import export_analysis
from test_regression import fixture, run
from test_hardening import disappearance
from data_pipeline import D, G, N, T, P, C


def examples(output):
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    locations = [
        '12 Rustaveli Avenue', '24 Chavchavadze Avenue', '8 Abashidze Street',
        '17 Pekini Avenue', '31 Vazha-Pshavela Avenue', '6 Tsereteli Avenue',
        '44 Aghmashenebeli Avenue', '9 Marjanishvili Street', '15 Kazbegi Avenue',
        '3 Paliashvili Street', '22 Tsotne Dadiani Street', '5 Queen Tamar Avenue',
    ]
    rows = []
    for month, factor in [('July', 1.0), ('August', 1.05)]:
        for i, address in enumerate(locations):
            rows.append(fixture(f'DEMO-{i+1:02}', month, **{
                'Store Name': f'Demo Pharmacy {i+1:02}',
                'Store Address Address': address + ', Tbilisi, Georgia',
                D: 120 + 15*i, T: 350 + 25*i, N: 3500 + 220*i,
                P: 20 + i, C: 8 + i, G: (2000 + 600*i) * factor,
                '% CVR': .055 + i * .01,
            }))
    outputs = []
    for name, a in [('Presentation_Polish_Multi_Store', run(rows)), ('Presentation_Polish_Partial_Coverage', disappearance())]:
        path = output / (name + '.pptx')
        render(a, path)
        prs = Presentation(path)
        add_text(prs.slides[0], 'ILLUSTRATIVE UX FIXTURE — SYNTHETIC DATA', .8, 6.8, 11.5, .3, size=12, bold=True)
        prs.save(path)
        export_analysis(a, output / (name + '_audit'))
        outputs.append(path)
    return outputs


if __name__ == '__main__':
    for path in examples(sys.argv[1]):
        print(path)
