# V9_Beta2 final release report

## A. Build status

**PASS**, with the explicit validation boundaries below. Complete release source and V9_Beta2.zip delivered. No analytical regression fails.

## B. Tests

**301 passed / 0 failed / 0 errors / 0 skipped**. 239 carried-forward tests (approved contract and stale-snapshot migrations documented) plus 62 new Beta2 tests. The untouched extracted baseline originally had 230 passes, 8 failures and 1 error; see TEST_REPORT.md and baseline_tests_original.log. Do not interpret the final count as an unmodified legacy-suite result.

## C. Exact files modified

- CHANGELOG.md
- MANIFEST_SHA256.json
- README.md
- RELEASE.json
- beta_presentation.py
- beta_validation.py
- business_classification.py
- config.py
- main.py
- main_v2_1.py
- presentation.py
- presentation_hardening.py
- presentation_polish.py
- subbusiness_unit_data.xlsx
- tests/beta1_0_frozen_files.json
- tests/beta_baseline.json
- tests/dev6_1_1_frozen_baseline.json
- tests/dev6_1_presentation_baseline.json
- tests/dev6_golden.json
- tests/test_beta_presentation.py
- tests/test_beta_validation.py
- tests/test_presentation_hardening.py
- tests/test_regression.py
- tests/test_v2_1.py
- triage_exports.py
- triage_presentation.py

## D. Exact files added

- reports/DECK_VALIDATION.md
- reports/FILE_INVENTORY.json
- reports/FILE_INVENTORY.md
- reports/FINAL_REPORT.md
- reports/FLOWERS_UPTIME_REGRESSION.md
- reports/FROZEN_MODULE_HASHES.md
- reports/KNOWN_ISSUES.md
- reports/SBU_COMPATIBILITY.md
- reports/SOURCE_CHANGES.diff
- reports/TEST_REPORT.md
- reports/TOP_GMV_REGRESSION.md
- reports/V9_Beta2_FLOWERS_synthetic_layout.json
- reports/V9_Beta2_FLOWERS_synthetic_package.json
- reports/V9_Beta2_JEWELRY_layout.json
- reports/V9_Beta2_JEWELRY_package.json
- reports/V9_Beta2_PHARMACY_abc_presentation_replay_layout.json
- reports/V9_Beta2_PHARMACY_abc_presentation_replay_package.json
- reports/V9_Beta2_SUPERMARKET_synthetic_layout.json
- reports/V9_Beta2_SUPERMARKET_synthetic_package.json
- reports/V9_Beta2_Top_GMV_empty_state_layout.json
- reports/V9_Beta2_Top_GMV_empty_state_package.json
- reports/baseline_tests_original.log
- reports/benchmark_value_changes.json
- reports/beta2_full_tests.log
- reports/deck_generation.json
- reports/frozen_fixture_comparison.json
- reports/frozen_module_hashes.json
- reports/historical_test_manifests/beta1_0_frozen_files.json
- reports/historical_test_manifests/beta_baseline.json
- reports/historical_test_manifests/dev6_1_1_frozen_baseline.json
- reports/historical_test_manifests/dev6_1_presentation_baseline.json
- reports/historical_test_manifests/dev6_golden.json
- reports/runtime.json
- reports/sbu_comparison.json
- reports/test_manifest_migration.json
- requirements-beta2-tested.txt
- sbu_catalog.py
- tests/abc_evidence.json
- tests/beta1_1_benchmark_reference.xlsx
- tests/beta2_frozen_modules.json
- tests/beta2_frozen_outputs.json
- tests/build_beta2_examples.py
- tests/fixtures/abc_reference.pptx
- tests/test_beta2.py
- validation/V9_Beta2_FLOWERS_synthetic.pptx
- validation/V9_Beta2_FLOWERS_synthetic_audit/Beta_Validation_Partner.csv
- validation/V9_Beta2_FLOWERS_synthetic_audit/Beta_Validation_Schema.json
- validation/V9_Beta2_FLOWERS_synthetic_audit/Beta_Validation_Stores.csv
- validation/V9_Beta2_FLOWERS_synthetic_audit/Beta_Validation_Stores_V2_1.csv
- validation/V9_Beta2_FLOWERS_synthetic_audit/Business_Actions.csv
- validation/V9_Beta2_FLOWERS_synthetic_audit/Business_Classification.csv
- validation/V9_Beta2_FLOWERS_synthetic_audit/Business_Classification.json
- validation/V9_Beta2_FLOWERS_synthetic_audit/Classification_Rule_Trace.json
- validation/V9_Beta2_FLOWERS_synthetic_audit/Classification_Schema.json
- validation/V9_Beta2_FLOWERS_synthetic_audit/Classification_Summary.json
- validation/V9_Beta2_FLOWERS_synthetic_audit/actions.csv
- validation/V9_Beta2_FLOWERS_synthetic_audit/coverage.csv
- validation/V9_Beta2_FLOWERS_synthetic_audit/metric_records.json
- validation/V9_Beta2_FLOWERS_synthetic_audit/metrics.csv
- validation/V9_Beta2_FLOWERS_synthetic_audit/monthly.csv
- validation/V9_Beta2_FLOWERS_synthetic_audit/opportunities.csv
- validation/V9_Beta2_FLOWERS_synthetic_audit/partner_comparisons.csv
- validation/V9_Beta2_FLOWERS_synthetic_audit/reviews.csv
- validation/V9_Beta2_FLOWERS_synthetic_audit/run_audit.json
- validation/V9_Beta2_FLOWERS_synthetic_audit/sbu_history.csv
- validation/V9_Beta2_FLOWERS_synthetic_audit/store_history.csv
- validation/V9_Beta2_FLOWERS_synthetic_audit/stores.csv
- validation/V9_Beta2_JEWELRY.pptx
- validation/V9_Beta2_JEWELRY_audit/Beta_Validation_Partner.csv
- validation/V9_Beta2_JEWELRY_audit/Beta_Validation_Schema.json
- validation/V9_Beta2_JEWELRY_audit/Beta_Validation_Stores.csv
- validation/V9_Beta2_JEWELRY_audit/Beta_Validation_Stores_V2_1.csv
- validation/V9_Beta2_JEWELRY_audit/Business_Actions.csv
- validation/V9_Beta2_JEWELRY_audit/Business_Classification.csv
- validation/V9_Beta2_JEWELRY_audit/Business_Classification.json
- validation/V9_Beta2_JEWELRY_audit/Classification_Rule_Trace.json
- validation/V9_Beta2_JEWELRY_audit/Classification_Schema.json
- validation/V9_Beta2_JEWELRY_audit/Classification_Summary.json
- validation/V9_Beta2_JEWELRY_audit/actions.csv
- validation/V9_Beta2_JEWELRY_audit/coverage.csv
- validation/V9_Beta2_JEWELRY_audit/metric_records.json
- validation/V9_Beta2_JEWELRY_audit/metrics.csv
- validation/V9_Beta2_JEWELRY_audit/monthly.csv
- validation/V9_Beta2_JEWELRY_audit/opportunities.csv
- validation/V9_Beta2_JEWELRY_audit/partner_comparisons.csv
- validation/V9_Beta2_JEWELRY_audit/reviews.csv
- validation/V9_Beta2_JEWELRY_audit/run_audit.json
- validation/V9_Beta2_JEWELRY_audit/sbu_history.csv
- validation/V9_Beta2_JEWELRY_audit/store_history.csv
- validation/V9_Beta2_JEWELRY_audit/stores.csv
- validation/V9_Beta2_PHARMACY_abc_presentation_replay.pptx
- validation/V9_Beta2_SUPERMARKET_synthetic.pptx
- validation/V9_Beta2_SUPERMARKET_synthetic_audit/Beta_Validation_Partner.csv
- validation/V9_Beta2_SUPERMARKET_synthetic_audit/Beta_Validation_Schema.json
- validation/V9_Beta2_SUPERMARKET_synthetic_audit/Beta_Validation_Stores.csv
- validation/V9_Beta2_SUPERMARKET_synthetic_audit/Beta_Validation_Stores_V2_1.csv
- validation/V9_Beta2_SUPERMARKET_synthetic_audit/Business_Actions.csv
- validation/V9_Beta2_SUPERMARKET_synthetic_audit/Business_Classification.csv
- validation/V9_Beta2_SUPERMARKET_synthetic_audit/Business_Classification.json
- validation/V9_Beta2_SUPERMARKET_synthetic_audit/Classification_Rule_Trace.json
- validation/V9_Beta2_SUPERMARKET_synthetic_audit/Classification_Schema.json
- validation/V9_Beta2_SUPERMARKET_synthetic_audit/Classification_Summary.json
- validation/V9_Beta2_SUPERMARKET_synthetic_audit/actions.csv
- validation/V9_Beta2_SUPERMARKET_synthetic_audit/coverage.csv
- validation/V9_Beta2_SUPERMARKET_synthetic_audit/metric_records.json
- validation/V9_Beta2_SUPERMARKET_synthetic_audit/metrics.csv
- validation/V9_Beta2_SUPERMARKET_synthetic_audit/monthly.csv
- validation/V9_Beta2_SUPERMARKET_synthetic_audit/opportunities.csv
- validation/V9_Beta2_SUPERMARKET_synthetic_audit/partner_comparisons.csv
- validation/V9_Beta2_SUPERMARKET_synthetic_audit/reviews.csv
- validation/V9_Beta2_SUPERMARKET_synthetic_audit/run_audit.json
- validation/V9_Beta2_SUPERMARKET_synthetic_audit/sbu_history.csv
- validation/V9_Beta2_SUPERMARKET_synthetic_audit/store_history.csv
- validation/V9_Beta2_SUPERMARKET_synthetic_audit/stores.csv
- validation/V9_Beta2_Top_GMV_empty_state.pptx
- validation/previews/V9_Beta2_FLOWERS_synthetic_slide_13.png
- validation/previews/V9_Beta2_FLOWERS_synthetic_slide_14.png
- validation/previews/V9_Beta2_JEWELRY_slide_13.png
- validation/previews/V9_Beta2_JEWELRY_slide_14.png
- validation/previews/V9_Beta2_PHARMACY_abc_presentation_replay_slide_13.png
- validation/previews/V9_Beta2_PHARMACY_abc_presentation_replay_slide_14.png
- validation/previews/V9_Beta2_SUPERMARKET_synthetic_slide_13.png
- validation/previews/V9_Beta2_SUPERMARKET_synthetic_slide_14.png
- validation/previews/V9_Beta2_Top_GMV_empty_state_slide_1.png

## E. Frozen analytical module integrity

PASS. scoring.py, store_status.py, data_pipeline.py, analysis.py, coverage_guard.py, triage_config.py and formatting.py are byte-identical to the extracted baseline. Config analytical constants are unchanged. business_classification.py differs only in the release-version literal. Nine frozen full-output replays, including the 80-store golden fixture, match exactly. Hashes and source diffs are included.

## F. OLD versus NEW SBU comparison

29 identical ordered columns. 312 → 516 rows. 26 → 43 SBUs. No removals; 17 additions. The exact NEW workbook is the root production source. In addition, 56 existing OTHER cells differ beyond floating-point rounding; the supplied changes are retained and itemized. Updated-data results need not equal old-data results, while identical-input model behavior is preserved.

## G. All 43 supported SBUs

ALCOHOL, AUTOMOTIVE, BAKERY_PASTRY, BEAUTY_PERSONAL_CARE, BOOKS, BUTCHERY_CHARCUTERIE, CBD, COFFEE_TEA, CONVENIENCE, COVID_TEST, DAIRY_PRODUCTS, ELECTRONICS, FASHION, FISHERY, FLOWERS, FROZEN_FOOD, FRUITS_VEGETABLES, GOURMET, HOME_DECORATION, ICE_CREAM, INDUSTRIAL, INTERNATIONAL, JEWELRY, KIDS_BABIES, LOCAL_MARKET, ORGANIC_BIO, OTHER, PARA_PHARMACY, PETS, PHARMACY_OTC, PHARMACY_RX, SERVICES, SEX_SHOP, SPORTS_OUTDOORS, STATIONERY_DIY, SUPERMARKET, SWEETS, TOBACCO_HEATED_PRODUCTS, TOYS_GAMES, TRADITIONAL_TOBACCO, VAPES, VISION, WELLNESS.

All 43 exact lookups and August 2026 same-month selections pass. Unknown SBU fails cleanly. Available names come from sbu_catalog.supported_sbus(), not the optional icon map. No Streamlit app was built.

## H. Top GMV regression

PASS on all six required cases and additional nonfinite/missing/foreign-population/denominator cases. Real abc presentation replay: Chabua €11,211, Top 1, 100.0%; Varketili €0 / No Activity excluded. Reported partner GMV unchanged. The raw Pharmacy workbook is unavailable, so this is a real-deck presentation replay rather than a full raw-data analytical replay.

## I. FLOWERS regression

PASS. Uptime stays excluded from commercial Priority, Impact and overrides. No exceptions were invented for new SBUs.

## J. Uptime regression

PASS. Assessed 0% is included; blank stays missing; partial coverage remains visible; zero assessed eligible stores yields no aggregate. Activity/lifecycle conflict never silently becomes Closed.

## K. Representative decks

PASS: JEWELRY 21 slides, SUPERMARKET 21, FLOWERS 21, real abc replay 22, empty-state evidence 1. All 86 slides rendered. Package and layout checks return zero findings. Montserrat and the existing design are preserved. PowerPoint-native execution was not performed.

## L. Known issues

See KNOWN_ISSUES.md. Raw Pharmacy replay unavailable; some new SBU decorative icons absent; August CVR missing in supplied ICE_CREAM/PHARMACY_RX rows; legacy CSV field name retained; existing dense presentation structure unchanged. None is an observed analytical regression. Test-manifest migrations and the newly tested dependency versions are disclosed.

## M. Final readiness recommendation

V9_Beta2 is ready to become the frozen backend baseline for the Python Web MVP.

This recommendation covers the implemented backend and presentation compatibility scope, with the Pharmacy raw-workbook limitation explicitly retained. It is not a claim of native PowerPoint certification or validation on unavailable raw inputs.
