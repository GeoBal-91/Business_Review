# V9_dev6.1 — final regression result

**PASS: 80 tests, 80 passed, 0 failed, 0 errors, 0 skipped.** Final run: 7 September 2026. The resumed run completed validation and packaging without further implementation changes.

## Tested runtime

| Component | Exact tested version |
|---|---|
| Python | CPython 3.14.6 |
| Execution platform | Linux x86_64; Linux-6.18.35-x86_64-with-glibc2.39 |
| pandas | 2.3.3 |
| NumPy | 2.3.5 |
| openpyxl | 3.1.5 |
| python-pptx | 1.0.2 |
| Matplotlib | 3.10.8 |
| Pillow | 12.3.0 |

All 20 installed packages, including transitive dependencies, are pinned in `requirements-tested.txt`. Only the direct pandas pin changed from Dev6: 2.2.3 → 2.3.3. [pandas 2.3.3 explicitly supports Python 3.14](https://pandas.pydata.org/docs/whatsnew/v2.3.3.html).

Binary-only dependency resolution also passed for Python 3.14 / macOS ARM64; evidence is in `macos_arm64_resolution.txt`. Actual execution and rendering were performed on Linux, not native macOS or PowerPoint for Mac. The unchanged source workbook produces an openpyxl default-style warning; generation succeeds.

## Regression scope

The attached, untouched Dev6 baseline previously passed **49/49** tests. The release retains those 49 test slots and adds 31 Dev6.1 checks. Two existing assertions intentionally follow the specification: alternate CVR modes now assert rejection (Change A), and the Unknown status text assertion accepts uppercase dashboard badges (Change C). The KEEP UNCHANGED tests themselves were not edited.

| Specification / invariant | Result and evidence |
|---|---|
| A: official reported CVR | PASS: store scoring, partner/SBU session-weighted aggregation, proxy isolation, missing column rejection, missing-value incomplete assessment and zero-session observation handling. |
| B: partner store coverage | PASS: disappearing large store remains Unknown; current orders remain 100 versus 1,100 previously; MoM/YoY changes are suppressed; expected/present/missing counts and names are exported and displayed; no false −90.9% performance narrative. Both comparison endpoints and first-observation timing are covered. |
| C / §6: dashboard states | PASS: Active, material opportunity, incomplete, Unknown, Closed, No Activity, FLOWERS and low-volume Critical Observation. Raw rate and denominator remain visible without implying materiality. |
| C: independent drivers and trends | PASS: Main Action differs from Worst KPI; Main Action differs from Largest Exposure; available, unavailable and gapped six-calendar-month trends. |
| D / E: provisional and incomplete wording | PASS: partial-period warning appears on every slide; incomplete assessments use Leading known issue and Not assessed; missing-rate confidence percentages are suppressed while available denominators remain visible. |
| F: model isolation | PASS: paired is the default; simple-product decks carry the challenger label on every slide; both analytical score columns remain exported. |
| G: upgraded runtime | PASS: compilation, all 80 regressions, fresh PPTX generation, rendering and CSV/JSON checks under Python 3.14.6. |
| Frozen numerical engine | PASS: shrinkage constants 150/30/10; existing anchors/interpolation; weights .30/.30/.25/.15; 50% dominant-KPI protection; raw Critical Flag thresholds/denominators; no added flag points. |
| Frozen lifecycle and SBU rules | PASS: zero delivered orders may remain Active; no delivered-order eligibility cutoff; calendar-month closure logic, missing month, two zero-uptime months, reopened Active stores; valid Closed/No Activity routine Priority zero; missing evidence remains incomplete; FLOWERS uptime exclusion; healthy-history uptime restoration logic. |
| Frozen ranking and business interpretation | PASS: paired default, full precision, conservative non-additive headline exposure, separate opportunity/review lanes, six opportunities by default, Top GMV Stores naming and singular issue → recommendation → action linkage. |

`scoring.py` and `store_status.py` are **byte-identical to Dev6**, verified against saved SHA-256 values. A separate frozen comparison covers **80 deterministic stores**, matching numerical scores within 1e-10 and matching flags, drivers, rank order and actions exactly. These 80 stores are a compatibility fixture inside the 80-test suite, not an additional 80 tests or threshold calibration.

All 41 bundled input/asset files checked against the baseline are unchanged; see `unchanged_inputs_assets.json`. Original TC51–TC100 fixtures were unavailable and were not rerun. The evidence here is the complete supplied Dev6 regression suite plus the saved Dev6.1 fixtures.

## Fresh decks and visual verification

| Deck | Slides | Purpose / result |
|---|---:|---|
| `Partner_Business_Review_V9_dev6_1.pptx` | 20 | Fresh review from unchanged bundled workbooks; all slides rendered and visually reviewed. The redesigned FLOWERS Store Diagnostics is slide 19. |
| `dashboard_states.pptx` | 12 | Synthetic visual fixtures: healthy/material/incomplete/Closed/No Activity/critical states, independent drivers, missing trend points and missing-current store. Rendered; state layouts reviewed. |
| `partial_store_coverage.pptx` | 25 | Synthetic disappearance fixture; Executive Summary retains totals and visibly suppresses comparisons. Rendered; coverage warning/details and Unknown dashboard reviewed. |
| `provisional_challenger.pptx` | 20 | Synthetic partial-period simple-product example. Rendered; provisional/challenger banners reviewed and asserted on every slide. |

The main sample's automated canvas-overflow check passed: **“Test passed. No overflow detected.”** See `presentation_overflow.log`. This check is supplemented by visual review; it is not a claim of native PowerPoint application certification. The synthetic decks are available in `validation/ux_examples/` and the separate UX examples ZIP. They illustrate test cases, not real partner performance.

## Audit exports

Verified **10 CSV files and 2 strict JSON files** from the fresh bundled-data run: `stores`, `metrics`, `opportunities`, `coverage`, `partner_comparisons`, `monthly`, `store_history`, `sbu_history`, `actions`, `reviews`, `run_audit.json` and `metric_records.json`.

CSV schemas remain present for empty opportunities/actions. JSON contains no NaN/Infinity literals. The run identifies `V9_dev6_1`, official reported CVR and the paired model; its source hashes match the packaged production Python files. Full-precision CSV/JSON export tests pass. The bundled sample contains one Active FLOWERS store, zero material business opportunities and one opening-hours review; no extra opportunities were manufactured for the sample.

## Reproduction and boundaries

From the extracted source folder, install `requirements.txt` in a Python 3.14 environment, then run:

```bash
python -m compileall -q .
python validate.py
python main.py
python tests/build_ux_examples.py validation/ux_examples
```

Machine-readable test results and individual cases are in `regression_results.json`; the complete test log is in `regression.log`. Artifact hashes and export checks are recorded in `artifact_verification.json`.

**Priority ≥ 5 remains provisional and unchanged.** This release does not calibrate that threshold, add a secondary action system or initiate rollout. Numerical architecture remained frozen throughout the hardening and resumed validation work.
