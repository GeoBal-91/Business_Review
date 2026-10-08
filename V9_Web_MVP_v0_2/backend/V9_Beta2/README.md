# V9_Beta2

Compatibility release based on the current extracted V9_Beta1_1 project. The analytical model and V2.1 classification calibration remain frozen.

## Run

Use Python with the dependencies in requirements.txt. From this folder:

```sh
python main_v2_1.py --sbu JEWELRY --partner partner_data.xlsx --output Partner_Business_Review_V9_Beta2.pptx
python main_v2_1.py --list-sbus
python -m unittest discover -s tests -v
python tests/build_beta2_examples.py
```

The production benchmark is subbusiness_unit_data.xlsx at the project root. The included partner workbook is the extracted baseline's JEWELRY example. Supply the appropriate partner workbook and exact SBU for other runs. --benchmark accepts an alternate dataset. Use --analysis-only for audit exports without a deck.

## Backend integration

```python
from sbu_catalog import supported_sbus
from config import Settings
from analysis import run_analysis
from business_classification import classify

choices = supported_sbus()  # sorted tuple from the workbook, suitable for a dropdown
result = run_analysis(Settings(partner_sbu=choices[0], input_file="your_partner.xlsx"))
triage = classify(result)
```

Read data explicitly per request or manage cache invalidation in the future frontend. No import-time workbook loading, hardcoded availability list, alternate-SBU fallback or Streamlit app is introduced. Optional artwork mappings do not control SBU eligibility.

## Validation and history

See reports/FINAL_REPORT.md, reports/SBU_COMPATIBILITY.md and reports/FROZEN_MODULE_HASHES.md. Validation decks and their audit data are under validation/. The Pharmacy abc file is a real-deck presentation replay; its raw workbook is unavailable.

The old benchmark under tests/ is reference-only. Historical release documents, golden scoring fixtures, source decks and original hash manifests are retained as evidence and must not be mistaken for current production data. Historical test snapshots were explicitly migrated for the approved Beta2 changes; originals and the original baseline test run are retained in reports/.
