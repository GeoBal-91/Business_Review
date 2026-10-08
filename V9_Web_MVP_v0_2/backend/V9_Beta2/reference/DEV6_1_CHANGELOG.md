# V9_dev6.1 — specification-linked changelog

Controlled hardening release from the attached V9_dev6.zip (SHA-256 `5625a21012b6c87114964932b426f97989f264093d2bd414834a431ca88a2a7f`). No threshold calibration, rollout or unrelated product changes.

## Scoring

**No Priority formula, curve, shrinkage, weight, raw flag, lifecycle, uptime-history or ranking change.** `scoring.py` and `store_status.py` are byte-identical to Dev6. The paired model remains the default, Priority ≥5 remains provisional, six opportunities remain the default and every business recommendation/action still follows its singular ranked issue record.

**A — official scoring input contract:** only reported `% CVR` is accepted as official conversion. At store level the observation is retained; partner/SBU aggregation remains sessions-weighted. The old `converted_sessions` and `delivered_per_session` scoring options now reject with an explicit message. Delivered/session and its gap against official CVR remain separate diagnostic exports. Missing official CVR cannot fall back to the proxy. PNA/Cancels/AOV count-first rules are unchanged. A zero/missing-session store observation can remain visible as reported, while scoring still follows the existing denominator/coverage gates.

## Data-safety changes

| Specification | Implementation | Verification |
|---|---|---|
| **A** | Require reported CVR; separate proxy/reconciliation columns; remove alternate ingestion substitutions. | Store, partner and SBU source-of-truth tests; missing column/value; proxy rejection; existing count-first tests. |
| **B** | Per-calendar-month expected/present/missing store counts and names. Guard both endpoints of MoM/YoY; retain raw totals and suppress invalid changes/narratives/share comparisons. Export coverage.csv and partner_comparisons.csv. | Large-store disappearance fixture: current orders remain 100, missing store is Unknown, MoM/YoY changes null, visible warning, no false −90.9% decline. Previous-period gaps and new-store timing also tested. |
| **E** | Keep partial evidence, but only present confidence percentages for assessed available rates. Preserve n when the rate is unavailable. Official unavailable scores stay Not assessed. | Missing CVR/PNA confidence and incomplete dashboard assertions. |

The expected roster is conservative: first observation onward, without inferring that an absent row means closure. Stores that never appeared cannot be detected. No new like-for-like growth calculation is introduced.

## Presentation-only changes

| Specification | Implementation | Verification |
|---|---|---|
| **C / §6** | New state-aware Store Diagnostics dashboard: name/location/period; status/data/assessment badges; GMV/delivered/sessions/attempts; four KPI/reference/gap cards; Severity/Impact/Priority cards; independent driver explanations; confidence bars with n; six-calendar-month main-KPI trend; one recommendation card. | Healthy, material, critical, incomplete, unknown, Closed, No Activity and FLOWERS fixtures; differing driver cases; available/unavailable/gapped trends; rendered sample and fixture decks. |
| **C / §6** | Raw critical observations have their own visible review section. Closed/No Activity emphasize lifecycle and zero routine recovery. FLOWERS uptime reads “Hygiene only — excluded from business Priority.” Missing-current uptime is explicitly unassessed. | Raw cancellation rate/n shown below business threshold; Closed/No Activity and FLOWERS behavior checks. |
| **D** | Every explicitly partial-period deck slide has a prominent “PARTIAL PERIOD — PROVISIONAL ANALYSIS” banner. | Full-deck per-slide banner assertion and rendering. |
| **E** | Incomplete dashboards use “Leading known issue,” “Worst known KPI,” and “Largest known exposure”; recommendation area requests data review and retains the missing/conflicting evidence. Missing SBU CVR no longer leaks NaN into executive narrative. | Incomplete wording/confidence tests and missing-benchmark deck integration. |
| **F** | Simple-product calculation/export retained. Every simple-product deck slide is marked “EXPERIMENTAL / CHALLENGER MODEL”; default paired decks are unmarked. | Standard vs challenger full-deck assertions; both score columns retained. |
| **B** | Partial Store Coverage labels on partner executive/trend/comparison slides; coverage detail pages with expected/present/missing counts and names. | Complete disappearance-deck text assertions and visual review. |

**§11:** threshold 5 is unchanged and still described as needing business calibration. **§12:** no secondary action engine added; a compact Secondary watch remains a future UX option.

## Runtime / dependency changes — G

Only direct pin changed: **pandas 2.2.3 → 2.3.3**, which explicitly supports Python 3.14 ([release notes](https://pandas.pydata.org/docs/whatsnew/v2.3.3.html)). Other direct pins remain NumPy 2.3.5, openpyxl 3.1.5, python-pptx 1.0.2, Matplotlib 3.10.8, Pillow 12.3.0.

Actual tests and generation run on **CPython 3.14.6 / Linux x86_64**. The full tested transitive environment is frozen in requirements-tested.txt. Binary-only dependency resolution also succeeds for Python 3.14 / macOS ARM64; this does not claim native macOS execution.

## Regression evidence — §2 / §13

- Original attached Dev6 baseline: **49/49 passed** before changes.
- Dev6.1: **80/80 passed**, including all 49 existing test slots and 31 new checks.
- Two existing assertions intentionally migrate with this specification: the alternate-CVR contract test now asserts rejection (**A**); the Unknown badge text assertion accepts uppercase (**C**). All KEEP UNCHANGED tests remain unchanged.
- Frozen Dev6 comparison across **80 deterministic stores** verifies scores within 1e-10, flags, drivers, rank order and actions on the updated runtime. This is a compatibility fixture, not threshold calibration.
- Source compiled; fresh bundled-data PPTX generated; CSV/JSON exports checked. Visual state fixtures and final overflow results are documented in validation/REGRESSION_RESULT.md.

The original TC51–TC100 fixtures remain unavailable; no claim is made that they were rerun. No business validation of threshold 5 or wider rollout is included.
