# V9 Beta 1.0

Presentation and validation-readiness release based on the supplied V9_dev6_1_2 source. The analytical engine is frozen. The supplied BEAUTY_PERSONAL_CARE configuration and 18-store partner input are retained byte-for-byte.

## Run

From the extracted `V9_Beta1_0` directory, using Python 3.14:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-tested.txt
python main.py
```

The CLI defaults to `Partner_Business_Review_V9_Beta1_0.pptx` and its `_audit` folder. For another partner, pass `--partner`, `--benchmark`, `--sbu` and a unique `--output`. `--analysis-only` writes both the normal audits and Beta validation exports without a PPTX.

The analytical config default output filename and audit `version` remain inherited engine metadata, to preserve the frozen config/analysis files. The Beta CLI supplies the new presentation filename, and cover/closing slides identify V9 Beta 1.0. Notebook callers can supply an explicit Beta output path to `presentation.render`.

## What changed

Methodology now appears after Top GMV Stores and immediately before the merged Priority Opportunities & Actions section. Store-level Severity/Impact numbers stay in individual Diagnostics and audit exports. The merged action pages retain the exact existing store ranking, Main Action KPI, evidence, actions and intended effects.

Action Focus explicitly summarizes the full selected list on every page. One to four opportunities use one page; five use 3+2; six use 3+3; zero has an honest empty state. One/two-item pages use expanded cards. Action Plan remains separate for owner/deadline agreement; operational/data observations remain a separate lane.

The main presentation finishes at Thank You. An Appendix divider precedes Store Overview for partners with at least five known stores, followed by all individual Diagnostics. Overview pages use up to 12 rows, fewer for long addresses; store names link to their diagnostics. Operational/lifecycle statuses are read from the existing result.

Matrix colors, legend continuation, cohort note, Top GMV crown/concentration/current-data eligibility, current-coverage qualification, partial-period banners and challenger labeling are retained. The analytical engine, threshold and FLOWERS policy have not changed.

## Validate

```bash
python -m compileall -q .
python -m unittest discover -s tests -v
python tests/build_beta_examples.py validation/ux_examples
```

See `REGRESSION_RESULT.md` for exact test/environment results, analytical parity, intentional presentation snapshot changes, fixture counts and rendering checks. The legacy analytical golden fixtures remain unchanged. The original 134-test Dev6.1.2 suite passed independently; eight presentation-oriented test functions were updated for the requested Beta titles, placement, wording and snapshots. Beta adds 47 focused tests.

The upload contains a different partner input/SBU than the earlier shipped FLOWERS demo. Its old bundled-data snapshot expectations were stale even before Beta work. Beta's current-input expectations were computed independently with the untouched supplied Dev6.1.2 code; original expectations are preserved in `reference/DEV6_1_2_test_snapshots`.

## Account Manager validation

Every successful `export_analysis` call now also creates:

- `Beta_Validation_Stores.csv`
- `Beta_Validation_Partner.csv`
- `Beta_Validation_Schema.json`

All manual AM columns are empty. Read `BETA_VALIDATION_GUIDE.md` before collecting feedback; save reviewed copies separately because regeneration writes fresh templates. No automated judgment, threshold calibration or duplicate-store merging is performed.

The Priority ≥5.0 threshold remains provisional. This release prepares the real-partner validation round; it does not establish business validity or authorize wider rollout.
