# V9_dev6.1.1 — presentation patch changelog

Base: completed `V9_dev6_1.zip`, SHA-256 `c304da558937a1817b781176876df354050881eb05a75c5b36b008e858ade056`.

**The analytical/scoring architecture remains frozen.** This is a presentation patch, not a new analytical release. `scoring.py` and `store_status.py` are byte-identical to Dev6.1. No Severity/Impact/Priority formula, curve, KPI weight, shrinkage constant, dominant-KPI protection, flag, lifecycle rule, FLOWERS rule, uptime-exposure method, threshold, ranking, CVR contract, Action Plan logic or audit calculation changed.

## Presentation changes

| Request | Implementation |
|---|---|
| **§1 — identifiable Store Performance Matrix** | Distinct deterministic colors, assigned from sorted stable Store IDs. Native editable legend maps each color to full store name/address; no point-level store labels. Right-side legend area retains plot space; long legends continue without truncating names or progressively reducing type size. All plotted points and reference lines remain identical across legend continuations. |
| **§1 — preserve analytical meaning** | Exact existing Active/Complete matrix population, GMV X-axis, official reported CVR Y-axis, median active-store GMV and SBU CVR references retained. Existing footnote retained verbatim. Color encodes identity only. |
| **§2 — Top GMV Stores** | Retained existing six-row sort/selection and all business columns. Added ranked-row treatment, supplied `assets/goldCrownCelebration.png`, and a compact highlight panel. Actual displayed N and current-period GMV concentration are calculated dynamically. |
| **§2 — concentration safety** | Share = sum of displayed stores' GMV / current partner GMV. Fewer than six stores and singular wording are supported. Empty/missing/zero GMV or incomplete current coverage yields an explicit unavailable/not-assessed share, avoiding an invented percentage. This statistic has no scoring/ranking effect. |
| **§3 — visual methodology guide** | Eight light illustrated cards use existing project assets and editable text/shapes, with a highlighted Key takeaway / Remember panel. Dynamic benchmark month and peer-composition note retained. Paired/challenger meaning, provisional threshold, overlap caveat, incomplete-evidence/review separation and uptime/FLOWERS caveats remain explicit. |
| **§5–6 — preserve other presentation behavior** | Recommendations content/layout preserved; Action Plan and Store Diagnostics untouched. No new icon library, dependency, forecast or expected impact estimate. Closing slide identifies the presentation patch as V9_dev6.1.1. |

## Coverage guard

**§4 — current Partner-vs-SBU CVR interpretation:** presentation context reads the existing current-period coverage result. When stores are missing, the Executive Summary replaces the directional CVR card interpretation with the raw SBU rate and displays:

> Partner vs SBU CVR: Not assessed — incomplete store coverage.

The raw current partner CVR stays visible. Complete-current comparisons retain Dev6.1 behavior, including when only a historical period has a coverage gap. Existing MoM/YoY suppression is unchanged. No CVR, score, Priority or eligibility calculation is changed.

## Scope and verification

Production edits are limited to `presentation.py`, `slides_market.py`, `slides_stores.py`, plus new `presentation_polish.py`. Test/example builders and release documentation are added separately.

- **98 tests passed / 0 failed:** all 80 original Dev6.1 tests unchanged, plus 18 focused presentation/coverage checks.
- 17 preserved source/test/dependency files checked by SHA-256, including both frozen engine modules and the original test files.
- Existing 80-store golden numerical/flag/driver/ranking/action comparison passes.
- Two Recommendations slides match Dev6.1 XML exactly for the saved fixture.
- Fresh bundled-data output: all 10 CSVs and `metric_records.json` are byte-identical to Dev6.1; analytical content in `run_audit.json` is identical. Output-path/source-hash metadata appropriately identifies the new files.
- Fresh sample and synthetic UX decks rendered; targeted slide review and overflow evidence are in `validation/REGRESSION_RESULT.md`.

No runtime/dependency changes. The audit's analytical version remains `V9_dev6_1`; `RELEASE.json` separately identifies presentation patch `V9_dev6_1_1`. Priority ≥5 remains provisional and uncalibrated.
