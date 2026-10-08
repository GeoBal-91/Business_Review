# V9_dev6 — audit-linked changelog

Continues the interrupted Dev6 implementation on the supplied Dev5 archive. Original inputs and assets are preserved. The prior audit was not restarted.

| Audit finding | Dev6 change | Regression evidence |
|---|---|---|
| **F01 — missing/invalid data** | Validate raw counts, rates, dates and duplicate grain before aggregation; preserve missingness; incomplete official scores stay unknown. Reject impossible counts. Keep fixed eligible weights. | Missing activity/numerator/benchmark tests; invalid counts/dates; partitions; cohort coverage. |
| **F02 — CVR definition** | Explicit `reported`, `converted_sessions`, and `delivered_per_session` contracts. Default reported CVR is session-weighted; no silent delivered-order substitution. Reconciliation is exported. | Weighted CVR, count numerator and explicit proxy tests. **Upstream KPI agreement remains open.** |
| **F03 — unsafe closure / missing stores** | Lifecycle plus data-quality overlay; closure contradictions go to review. Inferred closure needs reliable consecutive-calendar evidence and operating history. Missing-current stores remain Unknown. | Conflict, inferred/prelaunch, reopening, missing-current and year-boundary tests. |
| **F04 — positive priority floor** | Remove 15% floor. Default metric-paired candidate; simple-product challenger also available. Low-exposure raw critical observations stay in review. | One-cancellation low-volume tests for both models; zero-delivered material conversion remains eligible. |
| **F05 — excluded FLOWERS driver** | Central policy governs business eligibility and uptime closure evidence; excluded uptime cannot select the primary business action. Hygiene has a separate action. | FLOWERS exclusion/toggle and CVR-action assertions. |
| **F06 — overlapping exposure** | Headline exposure/impact uses the maximum component. No incremental-order or financial-recovery promise. Main Driver uses paired severity/exposure; expose worst KPI and largest raw exposure separately. | Overlap-max, cancellation-versus-CVR action, GMV invariance, saturation/curve tests. |
| **F07 — inconsistent recommendations** | One issue record feeds rankings, every displayed recommendation and Action Plan. Cover all six selected stores; partner-average health cannot suppress their actions. | Six-action coverage, healthy-partner masking and multi-store deck integration. |
| **F08 — precision / formula / labels** | Rank/filter at full precision, render scores to two decimals with boundary notation; unknown is explicit. Formula copy follows model; remove misleading average-CVR labels. Missing share comparisons do not imply “unchanged.” | Threshold boundary, exported precision and missing-data deck checks. |
| **F09 — confidence / competing labels** | Per-metric denominator and shrinkage weight remain visible with flags. Commercial status is independent of operations. Remove competing legacy priority state. | Denominator checks, Growth Potential independence, score unchanged when flags are suppressed. |
| **F10 — benchmark period / peer quality** | Same-month scoring by default; explicit dated stale opt-in. Missing benchmarks produce incomplete scores. Flag impossible partner/SBU GMV share and suppress it. Disclose unknown peer composition. | Stale/no-common-period, reporting-period and share-scope tests. **Peer membership/self-inclusion remains unresolved in aggregate input.** |
| **Audit §6 — uptime restoration/cohort** | Use a documented healthy-history baseline when available; otherwise label observed-attempt fallback uncertain. Exclude closed/prelaunch from operating cohort and disclose coverage. Missing cohort uptime cannot yield a reassuring partial mean. | Restoration monotonicity, closed-cohort and missing-uptime checks. |
| **Audit §9 — architecture/evidence** | Explicit load → lifecycle → score → choose actions → render modules, safe imports, atomic PPTX save, full-precision CSV/JSON and hashes. Preserve market/partner narrative; rebuild store sections around shared results. | Import isolation, strict JSON export, bundled end-to-end and stress rendering. |

## KEEP UNCHANGED — explicitly regression checked

- Count-first aggregation for PNA, cancellations and AOV; conversion remains denominator-aware under the declared contract.
- CVR/PNA/Cancels k = **150/30/10**, all five Dev5 anchor sets, weights **.30/.30/.25/.15**, relative-excess benchmark floors, **95%** uptime target and **50% dominant-KPI protection**.
- Raw critical thresholds, denominator conditions and **no flag score bonuses**.
- **Active with zero delivered orders** when sessions or attempts exist; no delivered-order eligibility cutoff.
- Consecutive **calendar** months rather than last available rows; two zero months and missing intermediate months do not infer closure; reopening is Active.
- Valid Closed/No Activity stores have zero routine KPI-recovery priority, with review visibility where appropriate.
- Short material executive list (six by default), retained diagnostics, FLOWERS temporary exclusion policy, and honest **Top GMV Stores** naming.

Exact constants and anchors were frozen from Dev5 source, not reconstructed from the new implementation. Evidence is in `tests/dev5_calibration.json` and `validation/`.

## Calibration and validation limits

The paired formula and default threshold **5** are provisional. Both candidate scores are exported; synthetic comparisons test behavior, not business-optimal ranking. AM blinded ranking/outcome validation, upstream CVR agreement and SBU peer composition are still required. No claim is made that the unavailable original 50 fixtures were rerun. The checked runtime is Python 3.12, not a certification of Python 3.14/macOS.
