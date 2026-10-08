# V9 Beta 1.0 — Regression and readiness report

**Verdict: ready to begin the controlled 25–30 real-partner / Account Manager validation round.** The engineering and presentation gates passed. The 5.0 threshold remains provisional; business validity, calibration and wider rollout remain decisions for the subsequent validation round.

This report completes the interrupted run from its saved regression/render evidence. No completed implementation was restarted, no analytical calculations were changed during final packaging, and no Dev6.2 work was begun.

## 1. Regression result

| Suite | Total | Passed | Failed | Errors | Skipped |
|---|---:|---:|---:|---:|---:|
| Final Beta suite | 181 | 181 | 0 | 0 | 0 |
| Original completed Dev6.1.2, with its original inputs | 134 | 134 | 0 | 0 | 0 |

The final Beta suite contains the 134 existing test slots plus 47 focused Beta tests: 32 presentation tests and 15 validation/freeze tests. Eight existing presentation-oriented test functions were updated for intentional Beta presentation changes; existing analytical assertions were not edited. `tests/test_regression.py`, `tests/dev5_calibration.json` and `tests/dev6_golden.json` are byte-identical.

Final unittest execution: **98.951 seconds**; the regression driver recorded **100.18 seconds** including setup/reporting. Evidence: `validation/regression.log` and `validation/regression_results.json`.

Focused coverage includes final deck order; removal of both legacy standalone sections; exact selected actions/ranks; 0/1/4/5/6 opportunity layouts; absence of exact Severity/Impact from main action pages and retention in Diagnostics/audits; full-list Action Focus and Highest/Lowest wording; Overview thresholds and pagination at 5/12/13/25–30 stores; all store values and links; lifecycle and missingness presentation; partial coverage; Top GMV current-data eligibility; FLOWERS policy; singular/plural; blank AM fields; full precision; frozen source and analytical assertions.

### Supplied-input provenance

The untouched uploaded Dev6.1.2 ZIP initially passed **131/134**. The three failures were stale bundled-demo/config expectations: the upload already changed the default SBU from FLOWERS to BEAUTY_PERSONAL_CARE and supplied a different, 18-store partner workbook. The original completed release with its original inputs independently passed **134/134**. Beta preserves the uploaded config and workbooks byte-for-byte and compares their results to an independently executed untouched uploaded engine. No analytical change was made to resolve these baseline expectations.

Earlier development logs are retained for traceability. A first focused failure concerned a synthetic expectation: missing CVR alone does not redefine an existing operational Healthy state. The fixture was corrected to provide missing operational evidence, and an explicit regression preserves the original CVR-only behavior. No lifecycle/scoring fix was needed.

## 2. Tested environment

- Python: **3.14.6 (main, Jul 18 2026, 17:01:31) [Clang 22.1.3 ]**.
- Platform: **Linux-6.18.35-x86_64-with-glibc2.39**.
- Dependency pins are unchanged from Dev6.1.2. Exact installed versions follow and are also recorded in `requirements-tested.txt`.

| Dependency | Tested version |
|---|---|
| contourpy | 1.3.3 |
| cycler | 0.12.1 |
| et_xmlfile | 2.0.0 |
| fonttools | 4.64.0 |
| kiwisolver | 1.5.1 |
| lxml | 6.1.3 |
| matplotlib | 3.10.8 |
| numpy | 2.3.5 |
| openpyxl | 3.1.5 |
| packaging | 26.3 |
| pandas | 2.3.3 |
| pillow | 12.3.0 |
| pyparsing | 3.3.2 |
| python-dateutil | 2.9.0.post0 |
| python-pptx | 1.0.2 |
| pytz | 2026.3.post1 |
| six | 1.17.0 |
| typing_extensions | 4.16.0 |
| tzdata | 2026.3 |
| xlsxwriter | 3.2.9 |

The source tests and deck generation ran in Python 3.14.6 on Linux. Native macOS Python/PowerPoint was not executed. After the interrupted run, final packaging verified saved hashes, CSV/JSON contents, deck structure and rendering artifacts without recalculating analytical results. Those file-only checks used the primary workspace runtime; they do not substitute for the completed 3.14.6 regression.

## 3. Files changed versus the supplied Dev6.1.2

| Category | Files and scope |
|---|---|
| Modified production files | `main.py`: additive export call, Beta CLI/default output. `presentation.py`: version text, singular/plural and coverage-detail placement. `slides_stores.py`: Beta section integration, section titles, Appendix navigation. |
| Added production files | `beta_presentation.py`: methodology, unified actions, Action Focus and Overview; read-only presentation of existing results. `beta_validation.py`: additive manual-validation CSV/schema export. |
| Updated presentation tests | `tests/test_hardening.py`, `tests/test_integration.py`, `tests/test_presentation_hardening.py`, `tests/test_presentation_navigation.py`, `tests/test_presentation_patch.py`; eight explicitly recorded function changes. |
| Updated snapshot containers | `tests/dev6_1_presentation_baseline.json`, `tests/dev6_1_1_frozen_baseline.json`. |
| Added tests/helpers | `tests/test_beta_presentation.py`, `tests/test_beta_validation.py`, `tests/beta_fixtures.py`, `tests/build_beta_examples.py`, `tests/beta_baseline.json`. |
| Documentation and evidence | Beta README, changelog, release metadata, this report, validation guide, archived baseline snapshots, regression/parity/render/packaging evidence and generated decks/audits. |
| Unchanged analytical/runtime/input files | Core engine/config, coverage guard, formatting, Diagnostics, other analytical helpers, dependency files, assets and supplied workbooks. |

`validation/final_artifact_verification.json` verifies 60 frozen files. Core SHA-256 values:

| File | SHA-256 — identical in baseline and Beta |
|---|---|
| `scoring.py` | `902b8dcbe73d547613d0b2a0d411d286f3a667aaa775fa2da8d121ca3ff32aa8` |
| `store_status.py` | `18dc83f21aaa381dfc355a41b8826329bdfaa943a69d5d26ebcf4f33fcc9f63f` |
| `analysis.py` | `7d6faba3bbd92ebbaf6bdfcbfb40a41e0a40d5fefdc01015275ae28840cd455b` |
| `data_pipeline.py` | `7452734bdc8558de64a1edc70ddea7db23a68735dc3d0c92a014fc4784d80f0c` |
| `config.py` | `4429c63a3c0aeb0d5a6d88669bd96d1fff7bf25caec4c0ca61a270f1dfe9485c` |

## 4. Analytical golden-output comparison

Ten datasets were independently run with the **untouched supplied Dev6.1.2 code** and compared with Beta outputs for the same inputs/settings. Result: **100/100 legacy CSV files plus 10/10 `metric_records.json` files byte-identical**. All ten `run_audit.json` analytical payloads are exactly equal.

Compared CSVs: `stores`, `metrics`, `opportunities`, `actions`, `reviews`, `monthly`, `coverage`, `store_history`, `sbu_history` and `partner_comparisons`. This preserves Priority, Severity, Impact, Main Driver, Severity Driver, Impact Source, Critical Flags, eligibility, ranking and complete store/metric/action/review records.

Whole `run_audit.json` files are not claimed byte-identical: source hashes reflect the presentation/export changes and input/benchmark/output path metadata differs between isolated runs. Only those source-hash and path-only settings fields are excluded; all analytical payloads and other settings are compared. Evidence: `validation/dev6_1_2_analytical_parity.json`. Final packaging reverified all 110 saved export hashes and every run's source hashes against the delivered source.

The two original analytical golden JSON fixtures are unchanged. The uploaded-input baseline and original demo expectations are both retained with their provenance.

## 5. Intentional presentation snapshot refreshes

`validation/presentation_snapshot_refresh.json` lists **12 snapshot-entry changes** and the **eight presentation test functions** affected. They cover:

1. Updated source/test hashes for the requested presentation, CLI and additive export interfaces.
2. Replacement of the old Recommendations XML snapshot with a single four-item Priority Opportunities & Actions page; action/input fixture rows are unchanged.
3. The supplied config hash and bundled-export expectations, independently reconciled to the uploaded partner/SBU using untouched Dev6.1.2. These are input-origin changes already present before Beta work.
4. Assertions for methodology placement, new section names, singular wording and Appendix Overview insertion. Analytical assertions remain intact.

Original snapshot files remain in `reference/DEV6_1_2_test_snapshots/`. No numerical golden was recalibrated to accommodate Beta presentation changes.

## 6. Fresh decks and visual fixtures

The bundled input produced the **43-slide, 18-store, August 2026 BEAUTY_PERSONAL_CARE** sample `Partner_Business_Review_V9_Beta1_0.pptx`. Nine synthetic cases are clearly identified as illustrative. All 10 decks / **315 slides** were rendered to images.

| Dataset | Known stores | Selected opportunities | Slides | Render / overflow |
|---|---:|---:|---:|---|
| Uploaded Beauty Partner | 18 | 4 | 43 | PASS |
| One Store Healthy | 1 | 0 | 21 | PASS |
| Four Opportunities | 4 | 4 | 24 | PASS |
| Five Opportunities | 5 | 5 | 28 | PASS |
| Six Opportunities | 6 | 6 | 29 | PASS |
| Zero Opportunities | 2 | 0 | 22 | PASS |
| Partial Current Coverage | 2 | 1 | 25 | PASS |
| FLOWERS | 1 | 1 | 21 | PASS |
| Eighteen Stores | 18 | 6 | 43 | PASS |
| Thirty Stores | 30 | 6 | 59 | PASS |

The source package includes the real sample and normal/Beta audit exports. The UX archive includes all ten decks, their audits and every rendered slide. The standalone large example is the **30-store / 59-slide** synthetic deck. Its Overview uses 12+12+6 rows, preserves all stores and all 30 Diagnostics, and keeps non-assessed/lifecycle stores outside the plotted cohort where appropriate.

The real partner's long-address Overview uses 11+7 rows for readability. Four opportunities fit on one page. Five use 3+2, six use 3+3, and one/two-item pages use expanded cards. Main presentation closes at Thank You before Appendix content.

## 7. Rendering, overflow and navigation

All ten decks returned success from both the presentation renderer and slide overflow checker. All 315 slide images exist. Final artifact checks found **zero native shape-bound violations**, valid PPTX ZIP structures, correct final section placement, complete Diagnostics and valid Overview-to-Diagnostics links. Evidence: `validation/render_checks/results.json`, individual render/check logs, `validation/slide_inventory.json` and `validation/final_artifact_verification.json`.

Full-size visual inspection covered the required layouts and states across the fixture set: methodology, 1/2/3/4-item action pages, Action Focus, empty state, partial-coverage Executive/Partner-vs-SBU/Operational Health/Top GMV pages, FLOWERS, Matrix legend continuations/cohort notes, real long-address and 30-store Overview pages, closing/Appendix order, and representative active/inactive/unknown Diagnostics. No clipped or unreadable text was found in these inspected layouts. One/two-item spacing was polished, followed by the final 181-test pass and re-render/overflow checks for the three affected decks.

These checks do not claim native Microsoft PowerPoint/macOS rendering validation or guarantee arbitrary future address lengths/fonts. The current dense Matrix design remains unchanged for AM feedback.

## 8. Validation export examples

The sample `Beta_Validation_Stores.csv` has **18 rows / 74 columns**, including all requested identity, context, raw KPI, full-precision score, eligibility, rank, Main Action, recommendation, critical and scoring-status fields, plus existing diagnostic component fields. Its seven AM judgment columns are empty. The partner template has **one row / 12 columns**; reporting period and SBU are populated, while partner identity and every manual judgment remain empty.

All ten decks' validation exports were verified: every known Store ID is retained; manual fields are blank; displayed counts match the existing selected actions; JSON is valid without non-finite JSON literals. Selected rank refers to the existing executive opportunity list, six by default. Eligible stores beyond that limit retain eligibility without an invented selected rank. Missing analytical values remain blank.

`BETA_VALIDATION_GUIDE.md` and `Beta_Validation_Schema.json` define expected Yes / Partly / No responses, score meanings and units. Save AM-reviewed copies separately before regeneration, which intentionally produces fresh templates. No AM judgment, threshold calibration or duplicate merging is automated.

## 9. Residual Beta questions and readiness decision

- **Business validation is pending.** Priority ≥5.0 remains provisional; examine approximately 3–7 and AM false-positive/false-negative evidence. No calibrated Low/Medium/High bands exist.
- SBU/AOV/volume differences and severe FLOWERS downtime remain validation questions. No GMV weighting, new thresholds or FLOWERS scoring change was introduced.
- Dense Matrix legends and Appendix navigation above ten stores should receive AM feedback. The 18/30-store examples passed the available visual/layout checks.
- Native macOS/PowerPoint rendering remains an environment check for the validation team; the automated build/regression environment was Linux/Python 3.14.6.

**Ready for the specified controlled validation round.** Engineering parity and presentation-readiness checks passed. The next phase is evidence collection with real partners and AMs, followed by a calibration decision; the engine and provisional threshold remain frozen in this release.
