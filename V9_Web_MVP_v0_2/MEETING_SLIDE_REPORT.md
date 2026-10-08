# Meeting-ready performance and conversion slide

Installed in `V9_Web_MVP_v0_2`; presentation build `2026-09-18.2`.

Only the Partner Performance & Conversion Evolution slide was redesigned, using the user's PetFood meeting screenshot as the composition reference and the existing Partner Review fonts, colors and rounded KPI cards.

## Files changed

- `web/presentation_update.py`: compact left-side native combo charts; four right-side KPI cards; automatic interpretation below each card row; display-only above/below benchmark wording. Chart helper retains its original default sizing for other callers. Existing presentation/formatting helpers supply values, changes, qualification and colors.
- `web/version.py`: increment presentation build to invalidate cached downloads.
- `tests/test_presentation_update.py`: add KPI values/units/layout checks and positive, negative, equal, missing and incomplete-coverage benchmark wording checks.
- This report and `validation/meeting_slide/` contain the delivery and validation evidence.

No website design, upload flow, worker logic, frozen Beta2 files or other slide builders changed.

## Final slide

Slide 9 of the 19-slide representative deck:

- Left/top: monthly GMV yellow bars and delivered Orders green line.
- Left/bottom: monthly Partner Sessions yellow bars and Partner CVR green line.
- Right/top: current GMV and Orders, each with relative MoM change.
- Right/bottom: current Partner Sessions with relative MoM change; Partner CVR with pp MoM change and pp gap vs selected SBU benchmark.
- Top-row interpretation: GMV movement and relative order-volume/basket-size movement, only when available.
- Bottom-row interpretation: qualified Partner CVR benchmark gap.
- Missing calendar months/measurements remain blank native chart/workbook cells; lines break at missing values. No SBU CVR series is added.

Previous-period values come from the engine's guarded previous row. Missing previous data or zero relative-comparison denominator remains unavailable. Incomplete store coverage suppresses the aggregate benchmark assessment. All calculations, classifications, scores, ranks, audit outputs and eligibility remain owned by frozen Beta2.

The slide uses Partner Sessions consistently. CVR benchmark text uses `X.X pp below [SBU] benchmark` or `above`, with the existing equal/unavailable/coverage states.

Executive Summary, Growth Drivers, standalone Partner Performance Evolution, standalone Conversion Performance and Store Performance Matrix remain absent. The combined slide exists once. The original/visual comparison pairs and enhanced Operational Health remain intact.

## Verification

- Completed existing and extended web/UI/presentation suite: **25 tests, all passed**. Log: `validation/meeting_slide/tests.log`. This completed run was retained when work resumed; it was not rerun.
- Frozen baseline rechecked after installation: **282 files match exactly**.
- Old/new worker-generated representative comparison: **all other 18 slide XML payloads and their chart XML are unchanged**.
- **All 22 analytical audit files match** after normalizing only environment-specific input, output and benchmark file paths in run provenance. The separate `web_run.json` presentation build is expected to change. Details: `parity.json`.
- Representative deck generated using `web.services.invoke` and the actual isolated `web/worker.py` subprocess, then generated again from the installed target directory. Source/slide map: `worker_generation.json`.
- Full deck converted to PDF using bundled LibreOffice with Montserrat; slide 9 rasterized at 1800 pixels and visually inspected. No clipping/overlap found in charts, legends, monthly labels, KPI values, changes, benchmark text or interpretations.

## Outputs and limitations

- `validation/meeting_slide/PETS_meeting.pptx`
- `validation/meeting_slide/PETS_meeting_audit.zip`
- `validation/meeting_slide/previews/PETS_meeting.pdf`
- `validation/meeting_slide/previews/PETS_meeting-slide9.png`

The example uses the existing synthetic PETS regression data and actual bundled PETS benchmark. It demonstrates the requested PetFood meeting layout; its values are **not** claimed to be the real PetFood meeting data. No underlying PetFood workbook was supplied with the screenshot, and screenshot values were not inserted into the analytical data.

Visual validation used PDF/PNG renders, not desktop PowerPoint. The complete existing website visual system and other slide designs are preserved.
