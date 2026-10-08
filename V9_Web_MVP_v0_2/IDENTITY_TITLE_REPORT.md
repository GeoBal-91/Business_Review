# Partner display identity — final validation

Installed in `V9_Web_MVP_v0_2`, presentation build **2026-09-19.1**.

## Behavior

The manually entered Partner Name is presentation metadata. Seven exact title templates use it after analytical slide construction:

| Slide | Template |
|---|---|
| 1 | `[Partner Name] Business Review` |
| 4 | `[Partner Name] vs [SBU]` |
| 5 | `[Partner Name] vs [SBU] · Visual` |
| 6 | `[Partner Name] Growth vs [SBU]` |
| 7 | `[Partner Name] Growth vs [SBU] · Visual` |
| 8 | `[Partner Name] Share of [SBU]` |
| 9 | `[Partner Name] Performance & Conversion Evolution` |

All 19 generated slide titles were reviewed. The other titles describe generic SBU, operational or store-level analysis and remain unchanged. Only exact identity heading matches are replaced. Generic metric labels, subtitles, analytical fields, internal identifiers and audit labels are preserved. The named legacy standalone Partner Name textbox is removed if present. The cover has one natural business-review title.

Long names remain complete. Titles wrap and reduce their font size within the existing title rectangle, retaining the visual language and leaving the subtitle/content positions unchanged.

## Changed application files

- `web/presentation_update.py`: seven explicit title templates, title fitting, removal of the legacy standalone cover name.
- `web/version.py`: new presentation build invalidates previously cached download results.
- `tests/test_partner_name.py`: exact title assertions, long/Unicode coverage and preservation checks.

No analytical engine or web layout changes were made for this update. The previously completed meeting-slide layout remains in place.

## Automated validation

**26 tests passed**, including actual isolated web-worker generation and Streamlit interaction tests. See `validation/identity_titles/tests.log`.

Coverage includes PetFood, trimmed input, Georgian input, a long English name and a long Georgian name. Tests assert manual-name precedence over an exported Partner Name while retaining the exported analytical identity, all seven expected titles, both Growth templates, removal of the duplicate cover name, unchanged metric body XML and generic subtitles. A name containing the literal word “Partner” also verifies that replacement is not global.

Worker audit outputs match across all five names after normalizing only temporary input/output provenance paths. Web tests cover required-name gating, generation, changed-name result invalidation, reuse of analytical validation and clearing the form.

The frozen baseline check passed: **all 282 files match the uploaded V9_Beta2.zip exactly**.

An additional comparison of PetFood and long-Georgian BEAUTY decks found **all 19 slide bodies identical after excluding identity title shapes**, and **49 chart, embedded-workbook and media parts unchanged**. For embedded XLSX containers, comparison ignores ZIP packaging timestamps and normalizes only created/modified timestamps in document properties. Worksheets, chart data and other payloads are compared exactly. See `validation/identity_titles/content_preservation.json`.

The retained combined-slide tests confirm absent legacy slides, missing-value behavior, chart series and benchmark wording. Analytics, growth calculations, SBU logic, scoring, filtering and audit data are unchanged.

## Visual validation

Actual worker-generated PPTX files were converted to complete PDFs using bundled LibreOffice. All seven affected slides were rasterized and visually inspected for each of these three cases:

- PetFood with BEAUTY_PERSONAL_CARE.
- `პეტფუდი — შინაური ცხოველების კვებისა და ვეტერინარული მომსახურების ცენტრი` with BEAUTY_PERSONAL_CARE.
- `PetFood & Friends — Premium Pet Nutrition, Accessories and Veterinary Care Georgia` with JEWELRY.

No clipped titles or overlap with subtitles/content were found. Full long names, Unicode characters and the “· Visual” suffix are visible. The cover has no redundant standalone name. The long-Georgian combined slide was also inspected in full to confirm its charts, KPI cards and interpretations remain clear.

Visual inspection used PDF/PNG renders, not desktop PowerPoint. Font substitution on another machine can affect rendering.

## Deliverables

In `validation/identity_titles/`:

- `PetFood_BEAUTY.pptx` and `PetFood_BEAUTY_audit.zip`.
- `Long_Unicode_BEAUTY.pptx` and `Long_Unicode_BEAUTY_audit.zip`.
- `Long_Name.pptx` and its audit ZIP, plus other name-regression decks.
- `previews/`: complete PDFs, individual affected-slide PNGs and title contact sheets.
- `worker_checks.json`, `content_preservation.json`, `tests.log`.

These are title/layout validation examples generated from the bundled sample workbook with selected benchmarks. They are not real PetFood business results. The sample values were not changed to match the meeting screenshot.

Generate a new presentation in the updated app to obtain these titles. Previously downloaded PPTX files are not rewritten.
