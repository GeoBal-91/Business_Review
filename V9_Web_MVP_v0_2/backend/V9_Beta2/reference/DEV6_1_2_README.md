# V9_dev6.1.2

Final presentation hardening of the completed Dev6.1.1 release. The analytical engine is frozen. See `CHANGELOG.md`, `RELEASE.json` and `validation/REGRESSION_RESULT.md`.

## Run

From the extracted `V9_dev6_1_2` directory:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py --output Partner_Business_Review_V9_dev6_1_2.pptx
python validate.py
```

The sample PPTX and its normal `_audit` directory are included. The existing CLI/config default output filename and analytical audit version remain Dev6.1; the explicit command above names this presentation patch. Existing `--partner`, `--benchmark` and `--sbu` options remain available.

## Changes

- Current partial store coverage qualifies all current partner-level SBU comparisons, including AOV/CVR/PNA/Cancels and aggregate Uptime/target context. Raw partner values and raw references remain visible. Historical-only coverage gaps do not suppress complete current comparisons.
- Top GMV Stores displays up to six stores with observed finite current GMV, retaining the original ranking keys. Observed zero remains valid; missing-current/Unknown stores stay in diagnostics/review/coverage instead of this ranking.
- Recommendations retains the existing ordered action records and adds an Action Focus summary for each displayed page. Review-item counts concern those stores and remain separate from Priority. Empty results have an explicit empty-state slide.

Matrix identity/legend, crown, dynamic concentration, visual methodology guide, Store Diagnostics, partial-period banners and challenger labeling are preserved. Existing recommendation content and Action Plan logic are unchanged. Text/cards remain native editable PowerPoint elements; existing plots and supplied artwork retain their image-based rendering.

Methodology appears immediately after the cover. The main review ends at Thank You; all Store Diagnostics follow an Appendix divider. Every matrix slide shows dynamic plotted/separate-review cohort counts. Recommendations pagination is 1–4 on one slide, five as 3+2 and six as 3+3.

## UX examples

```bash
python tests/build_hardening_examples.py validation/ux_examples
```

Synthetic full-review decks demonstrate complete coverage with six recommendations and two No Activity stores, four recommendations on one slide, partial coverage with one valid Top GMV store and one missing-current store, and a zero-recommendation partner. A focused two-slide example demonstrates five recommendations as 3+2. Their slides disclose synthetic data; each has normal audit exports. The principal sample uses the unchanged bundled workbooks. Selected PNG screenshots accompany the examples.

All 98 original test definitions are retained byte-for-byte. Only the presentation snapshots for the requested redesign/qualification were refreshed, with old expectations archived; 36 focused tests add independent content/order, coverage and frozen-engine checks.

Dependencies are unchanged from Dev6.1.1. Tested versions and platform are recorded in the regression report. Native macOS/PowerPoint for Mac execution is not claimed. The complete input/scoring documentation remains in `reference/DEV6_1_README.md`.

Priority ≥5 remains provisional. The next step is real-world business validation; this patch introduces no analytical redesign or threshold calibration.
