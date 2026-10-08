# Beta2 inspection and integration decisions

## Source of truth

The referenced ChatGPT attachment `V9_Beta2.zip` was retrieved from its local attachment cache because `/mnt/data` is not the filesystem used by this Mac session. No reconstructed or newer extracted build was substituted. `baseline_manifest.json` records the attachment SHA-256 and all 282 member-file hashes. The complete `backend/V9_Beta2` directory matches those bytes.

## Real project structure and entry points

Beta2 is a flat Python module project, not an `engine/` package. Its configuration resolves assets and default workbooks relative to `config.py` via `BASE_DIR`.

- `main.py`: legacy analysis/export/render CLI; returns the analysis result.
- `main_v2_1.py`: production Beta2 CLI preserving V2.1 classification; analysis → classify → export_triage → triage_presentation.render.
- `config.Settings`: frozen dataclass; explicit partner workbook, benchmark workbook, SBU and output path. Defaults retain reported CVR, paired priority, zero-month benchmark lag, no additive partitions and no partial-period reporting.
- `data_pipeline.load_data/load_frames/prepare_input`: ingestion, schema/content rules, date parsing, identity normalization and aggregation.
- `analysis.run_analysis`: the single analytical entry point.
- `business_classification.classify`: separate preserved V2.1 business classification.
- `triage_exports.export_triage`: complete audit exports, including original Beta exports.
- `triage_presentation.render`: final PPTX generation.

The web process does not import flat backend modules, avoiding module-name collisions in Streamlit. An isolated child places the exact backend directory first in its import path.

## Dependencies

Original pinned dependencies are pandas 2.3.3, numpy 2.3.5, openpyxl 3.1.5, python-pptx 1.0.2, matplotlib 3.10.8, Pillow 12.3.0. They are unchanged. Streamlit 1.62.0 is added. The full tested transitive set is in `requirements-lock.txt`. Python 3.12.14 on Apple Silicon was used for testing.

## SBU source/API

`subbusiness_unit_data.xlsx` at the Beta2 root is the production dataset. Its SHA-256 is `126b90a0b3daedf780105a50e8717afddca3089ca069fb9a6b0f6f32972b0b5b`.

`sbu_catalog.supported_sbus(source=SUBBUSINESS_FILE)` returns a sorted tuple of canonical SBU names from `Store Sub Business Unit`. It reads explicitly on invocation; importing the module does not read the workbook. Current result: 43 SBUs. Artwork mappings do not restrict eligibility.

The backend validates the selected SBU and filters its rows. It computes the latest partner month, rejects incomplete/future months by default, and selects an allowed benchmark with default lag zero. Missing same-month benchmarks are backend warnings; unknown benchmark metrics remain missing. The web readiness gate blocks missing same-month rows and missing CVR/PNA/Cancels benchmark metrics. This gate changes whether the UI permits a request, never Beta2 scores or classifications.

## Metadata and validation

The first XLSX sheet is read by Beta2. Required fields: Month, Year, # Delivered Orders, Sessions Store, Number of Total Orders, Number of Pna Orders, Number of Canceled Orders Due to Partner, € GMV, % Uptime, % CVR, plus Store ID or Store Address Address. Benchmark inputs additionally require Store Sub Business Unit.

Beta2 rejects duplicate normalized columns, invalid dates/counts/rates, duplicate store-month grain, contradictory count scopes and invalid lifecycle/reliability fields. It preserves supported missing-value warnings. `load_data` exposes normalized raw rows, reporting period, benchmark period, issues and input hashes. The web displays this information and computes only display identity/count metadata, never commercial metrics.

The supplied JEWELRY workbook has one address-based store and August 2026 as its latest month. It has no partner-name field. Guessing a brand from that address would be unsupported, so missing identity is shown explicitly.

## PPTX and logo path

`triage_presentation.render` first calls `presentation.render` to build the Beta narrative, then adds/replaces V2.1 classification content and saves the final deck. The original output size is 13.333 × 7.5 inches. The JEWELRY smoke run produced 21 slides.

`theme.PARTNER_LOGO_FILE` is a fixed `BASE_DIR / 'Partner Logo.png'`; `slides_market` imports it by value. The worker sets this rendering-only variable to the normalized uploaded PNG **before importing the slide renderer**. Each worker has its own process, so concurrent users cannot overwrite that setting. Glovo branding and all analytical Settings remain as supplied.

## Audit outputs

`export_triage` includes `main.export_analysis`, `beta_validation.export_validation`, business classification CSV/JSON, business actions, validation stores, rule trace, summary and classification schema. These include full-precision store/metric/opportunity/monthly/history/coverage/actions/reviews files, run_audit.json and metric_records.json. Source hashes and input hashes are retained by Beta2. The ZIP packages every file written into the run audit folder; `web_run.json` adds only UI provenance and logo hash.

Original run_audit Settings contain temporary absolute input/output paths. They are historical provenance, not persistent files that remain available after generation. The input hashes remain the stable identifiers.

## Temporary-file behavior

- `presentation.render`: creates `dev61-charts-*` TemporaryDirectory, saves an adjacent `.tmp.pptx`, atomically replaces its target, removes partial `.tmp.pptx` in finally.
- `triage_presentation.render`: creates `beta11-render-*` TemporaryDirectory for a baseline PPTX, then saves final output directly. A failure can otherwise leave outputs from earlier stages.
- Audit exports write a directory of CSV/JSON files directly; the CLI does not clean these up.
- The web wrapper encloses all of these in an outer `v9-web-*` TemporaryDirectory, sets child TMPDIR/TEMP/TMP and MPLCONFIGDIR inside it, and runs with that private working directory.
- The parent waits with a deadline; Python kills/waits for a timed-out child, then removes the directory. Success returns only PPTX/audit bytes and validation metadata.
- Bytecode writes are disabled in the child. The baseline is not used as a working output directory.

This provides cleanup for handled failures and normal operation, not guarantees after process force-kill or OS crash. No background service or history store was added.
