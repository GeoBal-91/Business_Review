# V2.1 implementation notes

## Separation and compatibility

`classify(AnalysisResult)` creates a separate TriageResult with enriched stores, selected triage actions, traces and summary. It never writes into the supplied result. No old production module imports the new layer; `main_v2_1.py` composes the unchanged engine, classification, additive exports and presentation adapter.

Original stores, metrics, opportunities, actions, reviews and summary retain their values and order. The new ACTION subset uses the frozen sort keys: Priority descending, Impact descending, Severity descending, Store ID ascending. Overrides enter this separate subset below 5, without changing original opportunities. Triage Rank identifies the new list. The six-item default limits presentation selection, not classification/audit retention.

Old CSV and metric-record JSON bytes remain reproducible. run_audit.json retains its analytical payload; source hashes additionally list new modules, and path-only settings reflect the installation. The inherited engine-version metadata is deliberately preserved; separate classification metadata identifies V2.1 / Beta 1.1.

## Assessability and floors

Only complete current paired-model assessments receive business classes. Missing current, insufficient evidence, data review, Closed and No Activity are UNCLASSIFIED with separate states. A zero-denominator `No exposure` record is complete evidence of no exposure, not missing data and not an adverse domain.

Operating count includes current Active stores with any positive observed delivered orders, sessions or attempts. An Active store with incomplete KPIs still counts if activity exists, avoiding an artificially single-store partner. No Activity, Closed, Unknown/missing and lifecycle-only rows are excluded.

Commercial adverse domains: CVR below SBU; PNA/Cancels above SBU; uptime below 95%. Qualification: sessions ≥50 for CVR; attempts ≥10 for PNA/Cancels; assessed uptime. FLOWERS uptime is never a commercial domain.

## Rules

Every rule is evaluated for metadata. First match supplies Action Reason; later matches are Supporting Rule Matches. Incomplete states fail all outcomes.

| Rule | Priority entry | Additional requirements |
|---|---|---|
| BASE_PRIORITY | ≥5 | Complete eligible business assessment |
| SINGLE_STORE_OVERRIDE | [4,5) | One operating store; frozen Primary KPI passes its evidence floor |
| MULTI_KPI_ESCALATION | [4,5) | ≥2 qualified adverse domains; ≥1 qualified severe KPI |
| SEVERE_PRIMARY_CORROBORATION | [3.5,5) | Severe CVR, sessions ≥50, meaningful commercial operational corroboration |
| BUSINESS_MATERIALITY_OVERRIDE | [3,5) | Assessed materiality; ≥2 qualified adverse operations; ≥1 material operational condition |

Severe CVR: ≤0.6×benchmark and gap ≤−3 pp. Severe PNA: ≥2×benchmark and ≥20%. Severe Cancels: ≥2×benchmark and ≥15%. Uptime ≤85% severe; (85%,90%] materially adverse; (90%,95%) adverse. **85.2% is not severe.**

Corroboration: adverse PNA/Cancels ≥1.25×benchmark OR gap ≥3 pp; uptime ≤92%. PNA/Cancels at 1–9 attempts can corroborate severe CVR but cannot independently become qualified ACTION domains. Zero attempts cannot corroborate.

Materiality: share ≥20%, OR top-two current GMV with delivered ≥20, sessions ≥200 or share ≥20%. Also require ≥2 qualified adverse operational KPIs and PNA/Cancels ≥1.5×benchmark OR uptime ≤90%. Top-two alone is insufficient. Incomplete current coverage or missing/non-positive partner GMV makes materiality unassessed; raw present-store share remains qualified by this flag.

Rate comparisons allow 1e−12 floating-point tolerance. Priority entry uses exact full precision, never rounded display values. Ratio-only corroboration/materiality against zero benchmark is not evidence; absolute-gap corroboration and absolute severe-rate guards remain available.

## Conservative interpretations to validate

- General override floors also apply to the Primary KPI for Single-Store; tiny cancellation evidence alone cannot bypass the floor through store count.
- Materiality requires complete current partner coverage, preventing inflated share from missing stores.
- Complete commercial evidence is required for classification; partial diagnostic evidence remains visible.
- PNA/Cancels can be separate domains only after each passes n≥10, not two domains from a tiny common denominator.
- V2.1 supports the frozen paired model and 5.0 base rule. A programmatic challenger/altered threshold is unassessed for this layer; legacy challenger exports remain accessible through the unchanged Beta interface.

## Isolated working defaults

The brief provides examples, not exact final tolerance/scale configuration. Defaults are therefore exported and labelled working assumptions, not newly claimed cross-SBU validation results.

| Setting | Default |
|---|---:|
| Negligible Priority | <1.0 |
| Maximum trivial CVR negative gap | 1.0 pp |
| Maximum trivial PNA positive gap | 0.5 pp |
| Maximum trivial Cancels positive gap | 0.5 pp |
| Minimum tolerated uptime | 93% |
| Low scale | Delivered ≤10 OR attempts ≤10 |
| Ultra-low scale | Delivered ≤2 OR attempts ≤3 |

HEALTHY also requires complete evidence, no commercial severe/material condition, and every adverse metric within its tiny-gap bound. Healthy Tolerance Candidate means tolerance actually accommodated an adverse metric. Configuration can make tolerances more conservative within these ceilings, not widen them.

Scale flags never affect classification or scores. Missing scale is not zero; Scale Evidence Available is exported. ACTION with low/ultra scale or low-n corroboration requires human review. Missing/data-review rows and unexplained inactivity remain reviewable. No GMV floor/weight, SBU score threshold or automatic calibration is introduced.

## Driver and action wording

Primary Action KPI copies frozen Main Driver. Likely Operational Driver is an investigation hypothesis from existing eligible evidence. Actions use availability/stock/order-execution context when supported; otherwise CVR prompts investigation of assortment/pricing/content/discoverability/funnel. Low-n PNA/Cancels explicitly remain corroboration with root cause unconfirmed. Narratives and scale flags never enter scoring. FLOWERS uptime remains hygiene and does not influence commercial override or commercial driver hypotheses.

The same selected triage action records feed action pages and Action Plan. All stores remain in Diagnostics/Overview/audits. Old Beta action CSVs stay unchanged; Business_Actions.csv describes V2.1 deck actions.

## Duplicate profiles

`calibration_summary(profiles, duplicate_profile_aliases)` accepts explicit aliases such as `{'FLOWERS #4':'FLOWERS #3'}` only when SBU, period, original/enriched contents and Store IDs match exactly. It skips the matching whole profile once. It never merges stores by address or KPI similarity. The tested 10-store mix is synthetic; real deduplicated counts require the missing real profiles.

## Presentation, runtime and evidence limits

The adapter appends replacement sections before removing originals, preventing duplicate PPTX parts. Expanded cards use up to two per page; Overview up to ten rows and fewer for long names. Frozen chart positions, assets, coverage guards, banners and Appendix diagnostics are retained.

Test host: Linux / Python 3.14.6 with unchanged pins. macOS PowerPoint/Keynote was not executed. All delivered slides were rendered and checked for slide-boundary overflow; changed and state-sensitive examples were visually inspected. This does not prove fit for arbitrary future long names or every viewer.

Complete retrospective seven-SBU inputs/AM labels were absent. Contract tests explicitly complete missing fields synthetically. No named-store exceptions, injected scores in delivered synthetic decks, retrospective agreement-rate claims or wider rollout are included.
