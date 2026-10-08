from pathlib import Path
import json
p=Path.cwd();v=p/'validation/final_release';m=json.loads((p/'releases/FINAL_RELEASE_METADATA.json').read_text())
text='''# Final release validation — 6 October 2026

**FINAL RELEASE VALIDATED — READY FOR PRODUCTION DEPLOYMENT**

Release-critical presentation preservation and identical-input analytical parity passed. No genuine regression introduced by this final task was found. Historical snapshot failures are accepted as documented pre-existing differences, per the user's release criteria; the full legacy suites are not represented as all green.

## Exact application/test changes

Paths below are relative to `/Users/giorgibalarjishvili/Desktop/V9_Web_MVP_v0_2`:

- `web/release_bookends.py` — new localized Cover/Thank You builders.
- `web/presentation_update.py` — invoke approved bookend builders; existing dynamic metadata and share-width behavior retained.
- `web/version.py` — final presentation version for generated-result invalidation.
- `tests/test_release_bookends.py` — new focused cover/closing checks.
- `tests/test_partner_name.py` — cover assertion reflects separate partner name and Business Review heading.

No backend source, analytical settings, assets, or external frozen-reference file changed during this task. Existing PNG artwork was reused unchanged. Only Cover and Thank You differ from retained presentation controls; all other slide XML and picture bytes match across five decks. Share chart remains exactly 20.0 cm, X 4.8 in, Y 1.45 in, H 4.6 in. Order and pagination are unchanged.

Additional generated artifacts are confined to `validation/final_release/` and `releases/`. Packaging adds RELEASE_README.md, requirements-final-tested.txt and SOURCE_MANIFEST_SHA256.json inside the archive; original runtime files are copied unchanged.

## Completed checks (not rerun unnecessarily)

| Check | Result |
|---|---|
| Web/presentation/UI | 37/37 PASS |
| Bundled backend historical suite | 299/301 PASS; 2 pre-existing logo snapshot mismatches |
| External frozen historical suite | 295/301 PASS; 6 pre-existing config/sample snapshot mismatches |
| Actual worker vs external engine | 5 cases × 22 analytical audit files = 110/110 equal after stated metadata normalization |
| Approved non-bookend slides | Exact slide XML and embedded picture-byte equality against retained controls |
| Native icon checks | 95 approved placements; all 8 asset files, 6 review types, summary mappings/coordinates, action and additional-action icons preserved |
| Worker cases | Actions_6 (38 slides), Empty (19), FLOWERS_missing (21), Long_Mixed_Unicode (22), Store_States (20) |
| Visual QA | 53 rendered slide previews; all required categories inspected |
| Clean archive | ZIP CRC and all 96 payload file SHA-256 checks PASS |
| Extracted archive actual worker | PASS; 19 slides/images identical; all 23 audit files including web provenance equal after path normalization |

### Pre-existing historical differences versus genuine regressions

Bundled backend failures: `test_beta_validation.FrozenDev612.test_engine_config_dependencies_assets_and_analytical_fixtures_byte_identical` expects an older Logo.png hash; `test_v2_1.ExportsAndFreeze.test_all_beta_source_tests_and_assets_unchanged` expects an older assets/glovo_logo.png hash. Current approved assets were not changed.

External reference failures are historical source-hash/default-fixture comparisons in test_beta_validation, test_presentation_hardening, test_presentation_patch and test_v2_1. External config defaults to PETS while the bundled default is JEWELRY; the external sample partner workbook also differs from historical controls. Config AST comparison confirms PARTNER_SBU is the only configuration-source difference. The same explicit SBU and identical input workbook were passed to both engines in each parity case. Frozen-reference files match the start-of-task snapshot. Neither baseline was edited to force historical tests green.

Audit normalization affects only temporary input/output/benchmark paths in run_audit.json and the config.py provenance hash associated with the verified default-SBU-only difference. All analytical values and remaining audit contents match; this is not a claim of raw ZIP-byte identity. Worker-only web_run.json is excluded from the 22 analytical files and is independently checked in package validation.

## Visual findings

Cover uses white background, teal rail, yellow accent, editable dynamic partner name, correctly spelled Business Review, dynamic period/SBU and uploaded partner logo. Long Georgian/Latin names remain intact. The representative upload is the retained Glovo-shaped partner-logo fixture, so the smaller Glovo graphic on its cover is the uploaded fixture, not a hardcoded duplicate.

Thank You uses yellow background, teal heading, dark supporting text, Glovo branding, pale existing decorative PNG and dynamic teal period pill. No partner name/logo/SBU is present. No new clipping, overflow, unintended font reduction, missing glyphs, checkerboard, halo or distorted PNG was found in changed slides.

Review summary Number → Icon → Label positions, row icons, generated Action Plan, Additional agreed actions, next check-in, zero-action behavior, long store names and pagination are preserved. Performance, opportunities, Discussion and share slides were inspected. No unapproved aesthetic changes were made. Existing automatic share-chart legend placement can approach/touch the series in sparse/near-flat edge cases; these chart pixels are identical to the approved pre-task controls and were not redesigned.

## Artifacts

'''
for label,rel in [('Representative actual Web Worker PPTX','decks/Actions_6.pptx'),('Long Unicode worker PPTX','decks/Long_Mixed_Unicode.pptx'),('Zero-action worker PPTX','decks/Empty.pptx'),('FLOWERS worker PPTX','decks/FLOWERS_missing.pptx'),('Store lifecycle worker PPTX','decks/Store_States.pptx'),('Extracted-package worker PPTX','decks/Packaged_Empty.pptx'),('Full representative PDF','previews/Actions_6.pdf'),('Cover','previews/Actions_6-1.png'),('Thank You','previews/Actions_6-27.png'),('Share evolution','previews/Actions_6-8.png'),('Performance/conversion','previews/Actions_6-9.png'),('Priority opportunities','previews/Actions_6-13.png'),('Operational review','previews/Actions_6-16.png'),('Generated action plan','previews/Actions_6-23.png'),('Additional agreed actions','previews/Actions_6-26.png'),('Discussion','previews/Actions_6-22.png'),('Long Unicode cover','previews/Long_Mixed_Unicode-1.png')]:
 f=v/rel;assert f.exists(),f;text+=f'- {label}: [{f.name}]({f})\n'
text+='\nEvidence: '+', '.join(f'[{n}]({v/n})' for n in ['verification.json','visual_qa.json','package_validation.json','web_tests.log','backend_tests.log','frozen_tests.log'])+'\n'
text+=f'''
## Release checksums

ZIP: `{m['zip']}`

ZIP SHA-256: `{m['zip_sha256']}`

Source manifest SHA-256: `{m['source_manifest_sha256']}`

Checksum file: `{m['zip']}.sha256`

## Validation limits

Visual QA used LibreOffice with Montserrat and Georgian fallback fonts; native Microsoft PowerPoint rendering was not independently exercised. Deployment itself and a fresh dependency installation were not performed. Extracted-package generation was verified using the existing tested Python 3.14.7 environment. The historical dependency lock differs in four installed versions (altair, contourpy, fonttools, lxml); the archive retains that lock and adds requirements-final-tested.txt plus release-specific setup notes recording exact tested versions. These environment differences are disclosed, not hidden as a clean-install test.

No further presentation or analytical changes are pending within the authorized final-release scope.
'''
(v/'FINAL_RELEASE_REPORT.md').write_text(text)
print(v/'FINAL_RELEASE_REPORT.md')
