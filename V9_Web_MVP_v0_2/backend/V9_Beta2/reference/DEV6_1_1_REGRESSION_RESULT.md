# V9_dev6.1.1 — final regression result

**PASS: 98 tests; 98 passed; 0 failed; 0 errors; 0 skipped.** This includes all 80 existing Dev6.1 tests, unchanged, and 18 targeted presentation/coverage tests.

The completed patch was restored from its recorded edits after the interrupted workspace reverted to an earlier snapshot. Validation and generated files were refreshed. No new implementation or analytical change was introduced during recovery.

## Tested environment

| Component | Exact tested version |
|---|---|
| Python | CPython 3.14.6 |
| Platform | Linux-6.18.35-x86_64-with-glibc2.39 |
| pandas | 2.3.3 |
| numpy | 2.3.5 |
| openpyxl | 3.1.5 |
| python-pptx | 1.0.2 |
| matplotlib | 3.10.8 |
| Pillow | 12.3.0 |

Dependency pins are unchanged from Dev6.1. All installed transitive versions are recorded in `requirements-tested.txt`. This run used Linux; native macOS/PowerPoint for Mac execution was not tested. Existing Dev6.1 macOS ARM64 dependency-resolution evidence is retained. The supplied workbook's unchanged default-style warning does not prevent generation.

## Targeted regression coverage

| Area | Tests | Result |
|---|---:|---|
| Matrix identity | 4 | Deterministic assignment independent of row order and values; distinct colors for up to 80 IDs; unchanged X/Y and references; no point labels; complete full-name/address legend with 28-store continuation fixture. PASS. |
| Top GMV display | 5 | Actual concentration numerator/denominator; original six-row ranking; fewer-than-six/singular case; zero/missing/empty GMV; incomplete-coverage share qualification. PASS. |
| Methodology guide | 3 | Actual benchmark period, missing benchmark, eight cards/caveats, FLOWERS and challenger wording. PASS. |
| Current-coverage CVR guard | 3 | Raw partner/SBU rates preserved and directional text suppressed when current coverage is partial; complete-current interpretation retained, including a historical-only coverage gap. PASS. |
| Frozen Dev6.1 behavior | 3 | Preserved source hashes; no render-time mutation of numerical records/actions; Recommendations content/layout XML identical. PASS. |
| Existing Dev6.1 suite | 80 | All original tests pass without edits, including KEEP UNCHANGED and the 80-store golden comparison. PASS. |
| **Total** | **98** | **98 passed; 0 failed.** |

## Frozen architecture evidence

`scoring.py` and `store_status.py` are byte-identical to the completed Dev6.1 release. The saved manifest checks 17 unchanged source/test/dependency files, including analysis, ingestion, coverage calculations, configuration, audit generation, formatting, Store Diagnostics, original tests and dependency pins.

The existing 80-store golden fixture continues to match numerical scores within 1e-10 and flags, drivers, ranking and actions exactly. This fixture is part of the 98-test suite, not an additional 80 tests or threshold calibration.

For the fresh bundled-data run, all **10 CSV exports plus `metric_records.json` are byte-identical to Dev6.1**. Analytical content in `run_audit.json` is identical; output-path/source-hash metadata changes appropriately. Both JSON files are strict JSON, and empty opportunity/action exports retain their schemas. Source hashes are checked against the packaged production files. All 41 bundled input/asset files checked against the baseline are unchanged.

Two Recommendations slides match the saved Dev6.1 slide XML exactly. The bundled 20-slide sample preserves 16 slide XML files exactly; only Matrix (12), Top GMV (13), methodology guide (17), and the closing presentation-version label (20) change. Complete-coverage Executive Summary remains unchanged.

## Fresh generation and visual checks

| Deck | Slides rendered | Reviewed locations | Overflow result |
|---|---:|---|---|
| Partner_Business_Review_V9_dev6_1_1.pptx | 20 | Matrix 12; Top GMV 13; FLOWERS guide 17; complete Executive Summary 7. | PASS |
| Presentation_Polish_Multi_Store.pptx | 33 | 12-store Matrix 12; Top GMV 13; methodology guide 19; complete Executive Summary 7. | PASS |
| Presentation_Polish_Partial_Coverage.pptx | 25 | Partial Executive Summary 7; Matrix 15; Top GMV 16; guide 21. | PASS |

All **78 slides** rendered successfully. Required slides were inspected at full size for legend readability, full store names, reference lines, crown/table balance, dynamic concentration, card text/caveats and partial-coverage wording. The 12-store legend fits on one slide without point labels. Nine selected screenshots are included in the UX examples ZIP.

Each of the three automated canvas checks reported **“Test passed. No overflow detected.”** Logs: `sample_overflow.log`, `multi_store_overflow.log`, `partial_coverage_overflow.log`. Visual review supplements canvas-boundary checks; the latter alone cannot certify every internal text layout in every future dataset.

The principal sample uses the unchanged bundled workbooks. Both additional decks use explicit synthetic fixtures and disclose this on their covers. Their normal audit folders accompany the UX examples. No sample opportunity or forecast was invented for the real bundled data.

## Reproduce

From the source folder after installing `requirements.txt`:

```bash
python -m compileall -q .
python validate.py
python main.py --output Partner_Business_Review_V9_dev6_1_1.pptx
python tests/build_presentation_examples.py validation/ux_examples
```

Evidence files: `regression.log`, `regression_results.json`, `artifact_verification.json`, `tests/dev6_1_presentation_baseline.json`, and the unchanged-input/asset manifest. Presentation patch identity is in `RELEASE.json`; the analytical audit version remains `V9_dev6_1`.

**Priority ≥5 remains provisional and unchanged.** No threshold calibration, Recommendations redesign, new analytical model or rollout is included.
