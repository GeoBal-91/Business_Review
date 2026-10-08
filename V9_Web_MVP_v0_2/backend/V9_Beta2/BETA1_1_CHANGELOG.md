# V9 Beta 1.1 changelog

Controlled V2.1 business-classification implementation above the supplied V9_Beta1_0. **This is not a new analytical engine.**

## Business classification — brief §§1–14, 17–18, 21–23

- Separate ACTION / MONITOR / HEALTHY / UNCLASSIFIED and operational/data states.
- Five rules in required precedence: Base Priority, Single-Store, Multi-KPI, Severe Primary + Corroboration, Business Materiality. Singular primary reason; supporting matches retained.
- Evidence floors, severe/material uptime bands, exposure-guarded GMV materiality. Partial current coverage does not provide an assessed materiality denominator.
- Isolated configurable working HEALTHY tolerance and low/ultra-low-scale review flags, without score changes.
- FLOWERS uptime excluded from every commercial override; hygiene stays separate.
- Explicit matching whole-profile aliases prevent calibration double-counting without merging store identities.

## Actions and presentation — brief §§15–16, 19–20

- Primary Action KPI remains frozen. Separate Likely Operational Driver and investigation wording are evidence-aware; low-n PNA/Cancels are corroboration, not proven cause.
- ACTION cards show rule reason, Primary KPI, evidence, driver, action, intended effect and scale context. Exact Severity/Impact stay in Diagnostics/audits.
- Action Plan consumes the same selected triage actions. Original engine action exports remain unchanged.
- Methodology explains classification versus ranking and the provisional base threshold.
- Appendix Overview adds Business independently of operational Status; Diagnostics add business metadata.
- Intentional pagination change: expanded V2.1 cards use at most two per slide for readability. Four actions use 2+2; five 2+2+1; six 2+2+2. One is expanded; zero has an honest empty state. Overall Action Focus stays consistent.
- Matrix, Top GMV, coverage guards, banners, review lanes, Appendix links and all Diagnostics retained.
- Fixed singular `1 ACTION store`. Replacement sections are appended before removing old slides to prevent duplicate PPTX part names.

## Exports, interface and tests — brief §§18, 24–25

- Additive classification CSV/JSON, selected business actions, rule traces, summary, schema and extended blank AM validation fields.
- Explicit new `main_v2_1.py` entry; legacy `main.py` remains byte-identical.
- Added 58 tests plus labelled contract/UX fixtures and immutable baseline hashes. No old tests or snapshots edited.
- No dependency changes; Python 3.14.6 with the original pins tested.

## Explicitly unchanged

All 20 old production `.py` modules, including scoring.py, store_status.py, analysis.py, data_pipeline.py, config.py, presentation.py, diagnostics.py and main.py, remain byte-identical. CVR, missingness, lifecycle, benchmarks, severity, shrinkage, exposure, Impact, paired Priority, weights, dominant protection, original ranking, Primary KPI, Critical Flags, precision, FLOWERS policy and provisional base threshold 5.0 are unchanged.

## Evidence boundary

HOME #2's corrected human label is ACTION and is tested as the Business Materiality rule contract. Complete retrospective seven-SBU inputs were absent. Actual real-input replay, synthetic contracts and engine-generated examples are distinguished in VALIDATION_CONTROL_COVERAGE.md. Conservative interpretations and working defaults are documented in IMPLEMENTATION_NOTES.md.
