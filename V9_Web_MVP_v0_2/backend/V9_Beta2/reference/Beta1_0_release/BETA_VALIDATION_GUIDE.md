# V9 Beta 1.0 — Account Manager validation guide

This build is for a 25–30 partner validation round. The Dev6.1.2 analytical engine is frozen. Priority 5.0 is provisional; this build does not calibrate it.

For each partner, generate a review with its correct SBU, keep the source inputs and `_audit` folder, and make a separate working copy of the two Beta validation CSVs before collecting AM feedback. Regeneration produces fresh blank AM fields; it does not merge prior feedback.

```bash
python main.py --partner your_partner.xlsx --benchmark your_sbu.xlsx --sbu BEAUTY_PERSONAL_CARE --output reviews/partner_01_V9_Beta1_0.pptx
```

`--analysis-only` also writes the validation files. All existing CSV/JSON audit files remain available beside the additional exports.

| File | Role |
|---|---|
| `Beta_Validation_Stores.csv` | Every known Store ID, including missing-current, inactive, incomplete and below-threshold stores, with exact existing analytical values and empty AM fields. |
| `Beta_Validation_Partner.csv` | One partner-level feedback row. Partner identifier is left manual; SBU and reporting period are copied from the analysis. |
| `Beta_Validation_Schema.json` | Expected manual values, data units and interpretation notes. |

Rates are exported as fractions, for example `0.2` = 20%. Severity, Impact and Priority are continuous 0–100 methodology scores, not percentages. Analytical values keep full precision. Blank analytical cells mean unavailable, not zero.

`Eligible Opportunity` is the existing engine eligibility flag. `Displayed Opportunity` and `Opportunity Rank` refer only to the existing selected executive list (six by default). An eligible store outside that limit retains its eligibility and has no invented displayed rank. All known stores are available for missed-opportunity review. `Recommended Action` is the exact selected action where present, otherwise the existing diagnostic Recommended Focus. Incomplete rows can carry a known diagnostic driver; this does not make them assessed business recommendations.

| Store feedback field | Expected response |
|---|---|
| `AM_Should_Be_Priority` | Yes / Partly / No |
| `AM_Rank` | Positive integer rank among known stores; leave blank if not ranked |
| `AM_Main_Action_KPI_Agree` | Yes / Partly / No |
| `AM_Action_Relevance_1_5` | 1 = not relevant; 5 = highly relevant |
| `AM_Important_Opportunity_Missed` | Yes / No |
| `AM_Should_Not_Be_Pitched` | Yes / No |
| `AM_Comment` | Free text, including an alternative KPI or missing business context |

Partner feedback records trust (1–5), top-opportunity alignment, main-action alignment, manual false-positive/false-negative counts, Action Focus usefulness, Appendix friction (1 = easy, 5 = high friction), narrative logic and notes. Alignment/narrative judgments use Yes / Partly / No; Action Focus usefulness uses Yes / No. All AM judgments start empty.

The validation analysis should later examine:

1. Top-opportunity and Main Action KPI agreement. Define how Partly responses will be handled before reporting agreement rates.
2. False positives: assessed Priority ≥5.0 but AM marks the opportunity irrelevant / should not be pitched.
3. False negatives: assessed Priority <5.0 but AM identifies an important material opportunity. Review missing/incomplete evidence separately; do not treat a missing score as a below-threshold score.
4. Scores around 3–7, retaining continuous raw scores. No Low/Medium/High Priority bands are defined.
5. SBU, AOV, volume and store-size differences using existing exported values. Do not add GMV weighting or SBU thresholds in this build.
6. Partner-facing trust, Action Focus usefulness, and Appendix navigation friction, especially above 10 stores.
7. FLOWERS severe downtime as a future validation question. Its current hygiene-only commercial exclusion is unchanged.
8. Similar store names/addresses as potential identity observations. Keep distinct Store IDs; do not automatically merge stores.

The Appendix overview is an operational/lifecycle comparison layer. A Healthy operational status can coexist with a conversion opportunity. Use Priority, KPI values, assessment completeness and the linked individual Diagnostics for full context. Overview display order does not change the opportunity ranking.

The operational/data review list is separate from business Priority. Critical observations, missing data, inactivity and opening-hours hygiene remain visible even when they are not selected commercial opportunities. Exposure is an opportunity signal, not a recovery promise or financial forecast.

Use AM evidence from the validation round to decide what to calibrate next. No calibration, rollout or Dev6.2 work is performed by this package.
