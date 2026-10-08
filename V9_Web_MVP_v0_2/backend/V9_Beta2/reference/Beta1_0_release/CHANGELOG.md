# V9 Beta 1.0 — Changelog

Beta 1.0 is a presentation / validation-readiness release. The analytical engine remains frozen from the supplied Dev6.1.2 source. Its next use is the controlled 25–30 real-partner / Account Manager validation round.

## Presentation changes

| Brief | Implementation | Files |
|---|---|---|
| 1–2: flow and methodology | Move the redesigned **How We Prioritize Opportunities** immediately after Top GMV Stores and before Priority Opportunities & Actions. Explain Severity, order-related Impact, KPI-level `Severity × Impact / 100`, the paired store combination, dominant-KPI protection, Main Action KPI and the provisional 5.0 threshold. Retain missing-evidence, 95% uptime, separate critical-review, conservative exposure and actual benchmark-period caveats. | `beta_presentation.py`, `presentation.py`, `slides_stores.py` |
| 3–4: unified action section | Replace standalone Biggest Opportunities and Recommendations pages with **Priority Opportunities & Actions**. Read the same selected AnalysisResult opportunities/actions, in the same order. Keep rank, full store name, Priority, KPI, evidence, exact action and intended effect. Exact store Severity/Impact remain in Diagnostics and audit exports. | `beta_presentation.py`, `slides_stores.py` |
| 5: pagination | Zero opportunities has an honest empty state. One to four use one slide; five use 3+2; six use 3+3. One/two-item pages use expanded cards; four use compact cards. Multi-page titles show page/total. | `beta_presentation.py` |
| 6: Action Focus | Repeat **Overall Action Focus** from the full selected action set, including Primary Action KPI, distinct Stores Requiring Action, **Highest / Lowest** Priority and relevant review-item count. Label review items as separate from business Priority. Keep the three Next Review steps. No new Priority bands or forecasts. | `beta_presentation.py` |
| 7–9: execution and Appendix | Keep Action Plan and Operational & Data Review separate. Move coverage-detail pages into the review section. End the main flow at Discussion / Thank You, then Appendix divider, Store Overview and every individual Diagnostic. Generate Overview for ≥5 known stores, with up to 12 rows per page and fewer for long addresses. Read current raw values and existing operational/lifecycle statuses; link store names to their Diagnostics. Overview sorting is a local display copy. | `beta_presentation.py`, `presentation.py`, `slides_stores.py` |
| 17, 21: wording/version | Use dynamic singular/plural, page indicators, continuous-score wording and visible **V9 Beta 1.0** on cover/closing. Default CLI output is `Partner_Business_Review_V9_Beta1_0.pptx`. | `beta_presentation.py`, `presentation.py`, `slides_stores.py`, `main.py` |

## Validation-readiness changes

| Brief | Implementation | Files |
|---|---|---|
| 15–16: additive exports | Every normal audit export, including analysis-only runs, also writes `Beta_Validation_Stores.csv`, `Beta_Validation_Partner.csv` and `Beta_Validation_Schema.json`. All known stores remain available, including unselected, below-threshold, inactive and missing-current stores. Existing values retain full precision/missingness; all AM judgments and manual partner identity start blank. | `beta_validation.py`, `main.py` |
| 16, 18: validation protocol | Document AM agreement, false positives/negatives, near-threshold 3–7 review, SBU/AOV/volume effects, trust, Action Focus and Appendix friction. No automated judgment, calibration or duplicate-store merging. | `BETA_VALIDATION_GUIDE.md`, `README.md` |
| 19–20: regression evidence | Add 47 Beta tests, independent ten-dataset analytical comparison, ten rendered decks, layout/navigation checks and explicit presentation snapshot-change evidence. Original analytical assertions and analytical golden fixtures remain unchanged. | `tests/test_beta_presentation.py`, `tests/test_beta_validation.py`, fixture/build helpers, `validation/` |

## Explicitly unchanged

- Scoring, benchmark logic, CVR contract, lifecycle, missingness, scoring eligibility, opportunity ranking and Main Action KPI selection.
- Severity curves; CVR/PNA/Cancels shrinkage constants 150/30/10; KPI weights 0.30/0.30/0.25/0.15; 50% dominant-KPI protection; exposure and Impact curves; paired Priority; raw Critical Flag rules and denominators.
- Priority ≥5.0 remains **provisional**. No threshold bands, SBU-specific thresholds, GMV weighting or recalibration.
- FLOWERS uptime exclusion and opening-hours review policy; healthy-history uptime exposure; conservative headline exposure; separate commercial and operational/data lanes.
- Matrix colors, full legend/continuation, cohort note and positioning; Top GMV eligibility, zero-GMV handling, crown and dynamic concentration; partial-coverage guards; partial-period banners; challenger labeling; individual Diagnostics.
- `scoring.py`, `store_status.py`, `analysis.py`, `data_pipeline.py`, `config.py`, dependencies, bundled inputs and the original analytical golden JSON files are byte-identical to the supplied baseline. No analytical implementation bug required a change.

## Snapshot and baseline provenance

Eight existing presentation-oriented test functions were adapted for the requested titles, flow, wording and merged-page XML. The complete list and 12 snapshot-entry changes are recorded in `validation/presentation_snapshot_refresh.json`; original snapshots remain in `reference/DEV6_1_2_test_snapshots/`.

The supplied ZIP already contains a BEAUTY_PERSONAL_CARE default and an 18-store partner workbook, differing from the earlier shipped FLOWERS demonstration. Three bundled-demo expectations were stale on that untouched upload. Current-input expectations were generated independently with untouched supplied Dev6.1.2 code. This is input provenance, not a Beta config or scoring change. Both supplied files remain byte-identical.

The normal audit's inherited engine version and config output filename are preserved inside the frozen modules. The Beta CLI chooses the Beta deck filename, and visible deck labels use V9 Beta 1.0.

## Release result

181 tests passed; 0 failed; 0 errors; 0 skipped. Across ten identical-input comparisons, 100 legacy CSVs and ten metric-record JSONs are byte-identical; all ten run-audit analytical payloads match. Ten decks / 315 slides rendered and passed overflow checks. See `REGRESSION_RESULT.md` for environment, fixtures, file changes and remaining validation questions.
