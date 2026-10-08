# V9 Web MVP v0.2 — Partner Insights

A local, fully Python Streamlit interface around the **unaltered uploaded V9_Beta2** backend. No scoring or classification formulas are implemented in the web layer.

## Run on your Mac

Tested with Python **3.12.14** on Apple Silicon. Use Python 3.12 for the same environment. If `python3.12 --version` is unavailable, install Python 3.12 from python.org (or `brew install python@3.12` if you already use Homebrew).

1. Download `V9_Web_MVP_v0_2.zip` into Downloads. Double-click it in Finder to extract it.
2. Open Terminal and run these commands, one line at a time:

```sh
cd "$HOME/Downloads/V9_Web_MVP_v0_2"
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python -m streamlit run app.py
```

3. Open **http://localhost:8501** if the browser does not open automatically.
4. To stop: press **Control-C** in Terminal.
5. For later starts:

```sh
cd "$HOME/Downloads/V9_Web_MVP_v0_2"
source .venv/bin/activate
python -m streamlit run app.py
```

If the extracted folder is elsewhere, replace the `cd` path with its actual location. In Finder, you can drag the folder into Terminal after typing `cd `.

The app uses Montserrat in the original decks. Install that font on the computer where you view the PPTX if you want the original typography; PowerPoint may substitute a font otherwise. Generation itself does not require PowerPoint or LibreOffice.

## First smoke review

- Upload `backend/V9_Beta2/partner_data.xlsx` (the original JEWELRY sample).
- Upload your logo, or use `backend/V9_Beta2/Partner Logo.png` for a test.
- Select **JEWELRY**.
- Expect **August 2026**, **1 store**, and partner **Not included in export**. This sample does not contain a partner name.
- Select **Generate Review**, then download both **PPTX** and **Audit ZIP**.

The sample is historical and remains usable once August 2026 is complete. The app never enables partial-period analysis.

## Configure the Looker button

Edit `web_config.toml` with a text editor:

```toml
looker_export_url = "https://your-company-looker-host/your-saved-export"
```

Or set the environment variable before starting:

```sh
export V9_LOOKER_EXPORT_URL='https://your-company-looker-host/your-saved-export'
python -m streamlit run app.py
```

The button is disabled until a valid HTTP(S) link is configured. It opens the link; it does not authenticate, fetch data, or call a Looker API.

## Accepted inputs and blocking rules

- Partner data: **XLSX**, first sheet, up to **20 MB** compressed / **150 MB** expanded. Export a single partner, one row per store/month. CSV and legacy XLS are not supported in this MVP.
- Logo: **PNG or JPEG**, up to **5 MB** / **16 megapixels**. Required before generation. JPEG orientation is respected and the image is converted to PNG for Beta2's fixed logo interface.
- SBU choices come directly from `sbu_catalog.supported_sbus()` and the bundled production benchmark (43 choices at release).
- Beta2 owns required columns, date parsing, percentage units, content checks, duplicates, rate/count contracts and complete-period validation. Rates use fractions such as `0.8` or explicit `80%` strings, per Beta2 defaults.
- The web gate additionally requires a same-month benchmark with known CVR, PNA and partner-cancellation rates. ICE_CREAM and PHARMACY_RX lack August 2026 CVR in this frozen workbook and are blocked for that month. No alternate SBU or older-period fallback is used.
- Missing partner measurements that Beta2 accepts remain warnings/unknowns; the web app does not invent zeroes or impose new scoring rules.
- Partner display checks `Partner Name`, `Partner`, `Store Partner Name`, then a single common `Store Name`. Multiple explicit partner names block generation. Multiple branch names do not identify a partner. If no unambiguous name exists, the app says so. This display metadata is never passed into scoring.
- Store count means unique Beta2-normalized store identities across the export. Latest-period row coverage is shown separately. A store missing in the latest period remains visible to Beta2's lifecycle/coverage rules.

A partner export without identity metadata cannot prove that all stores belong to one partner; select the correct single-partner export in Looker.

## What you receive

The PPTX first uses `triage_presentation.render`, the same V2.1 path as `main_v2_1.py`, then applies the web-only changes in `web/presentation_update.py`. Both original comparison slides remain, each followed by a visual version. A combined performance/conversion slide shows GMV with orders and partner sessions with partner CVR. Operational Health retains its text with added charts. Growth Drivers and Store Performance Matrix are omitted from the web deck. The Audit ZIP contains all files produced by `export_triage`: original CSV/JSON audits, Beta validation files, classification rows/actions, rule traces and summaries. An additive `web_run.json` records web metadata, the presentation adapter version and the normalized logo hash. The raw uploaded workbook and worker log are not included in the download.

## Isolation and cleanup

Each validation/generation runs in a separate Python process with a unique temporary directory. Uploaded data, logo, generated deck, audit files, chart scratch files, matplotlib cache and worker log are inside that directory. A `finally`-backed context removes it on success, validation failure, worker failure or timeout. Validation times out at 120 seconds; generation at 300 seconds.

Only the renderer's logo path is overridden, inside the child process, before slide modules import it. No frozen file is edited and the server never changes its working directory or shared renderer globals.

The presentation adapter edits the generated slide collection using existing theme and presentation helpers. It never modifies analysis results, classifications or audit exports. Missing months remain blank chart/workbook cells and break trend lines. FLOWERS uptime exclusions, partial-coverage qualifications and Top GMV eligibility remain owned by Beta2.

Only download bytes and validation summaries remain in session memory. No cross-session upload cache, database, login, saved history or direct Looker API is included. Change data, logo or SBU to invalidate results. **Clear uploads and results** releases the app's session references and resets upload controls. Already downloaded browser files remain on your Mac. Streamlit controls its own media/session-memory reclamation; clearing is not a claim of immediate secure memory erasure.

Normal exceptions/timeouts are covered. A force-kill or operating-system crash can interrupt cleanup and leave an OS temporary directory named `v9-web-*`; this MVP does not add a persistent cleanup daemon.

## Project layout

```text
app.py                       Streamlit entry point
web/services.py              Upload checks, subprocess bridge, download packaging
web/worker.py                Frozen-engine adapter and web readiness gate
web/presentation_update.py   Web-only changes to the generated slide collection
web_config.toml              Optional Looker URL
.streamlit/config.toml       Local bind, upload size and theme
requirements.txt             Direct dependencies, preserves Beta2 pins
requirements-lock.txt        Exact tested dependency versions
backend/V9_Beta2/             Complete uploaded baseline, byte-for-byte
baseline_manifest.json       Hash of every file from the uploaded ZIP
verify_baseline.py           Verify frozen baseline integrity
tests/test_web.py            Integration/UI/isolation/cleanup smoke tests
tests/test_presentation_update.py  Presentation and chart contracts
tests/build_web_presentation_examples.py  Representative decks and audit parity
INSPECTION.md                Backend interfaces and integration findings
TEST_REPORT.md               Actual checks and limitations
```

The backend's historical reports and example files are retained as supplied; they are not web-generated history.

## Verify and test

From the project folder with the virtual environment activated:

```sh
python verify_baseline.py
python -m unittest discover -s tests -v
```

The suite invokes real Beta2 generation, compares CSV audits to the untouched CLI, tests two simultaneous logos, and exercises Streamlit uploads, disabled generation, downloads and invalidation. It takes approximately a minute in the prepared local environment. No extra test dependencies are needed.

Generate the presentation QA examples with `python tests/build_web_presentation_examples.py`.
The decks and validation evidence are saved under `validation/presentation_update/`.
See `PRESENTATION_UPDATE_REPORT.md` for the completed presentation update, slide map,
fixture provenance, test results and visual-validation limitations.

For a new platform you can install `requirements.txt` instead of the full lock; that retains Beta2's six exact pins and the Streamlit version but resolves transitive dependencies again. The lock is the tested environment.

If installation fails, confirm Python 3.12 and internet access. If port 8501 is occupied, use `python -m streamlit run app.py --server.port 8502` and open http://localhost:8502.

Streamlit API references used: [download buttons](https://docs.streamlit.io/1.62.0/develop/api-reference/widgets/st.download_button) and [AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest).

## Web v0.2 design release

This release updates the Streamlit interface around the same unmodified 282-file Beta2 baseline. The worker bridge remains v0.1; its audit provenance continues to identify that adapter version. The user interface is v0.2.

- Glovo green/yellow workspace with the user-supplied logo and an original local SVG illustration.
- A single preparation form and a live review overview. The overview card is display metadata, not a rendered slide thumbnail.
- Three linked workflow stages, a readiness checklist, next-step links, and distinct warning/error/success states.
- The provided saved Looker report is configured in `web_config.toml`.
- Validation is reused when only the logo changes; any changed input still invalidates old downloadable results. Changing partner data or SBU reruns validation.
- Clear uploads and results resets data, logo, SBU and results.
- Downloads use detected partner/period in their filenames, with an explicit generic fallback when the export lacks a partner name.
- No new analytical rules, workbook edits, history, login or deployment.

`web/components.py` contains display helpers; `web_style.css` contains the design. Upload types/limits and all blocking conditions are unchanged.

The full local suite includes eight test methods, including a new regression check for logo changes reusing validation, invalid logos blocking generation, SBU changes requiring fresh validation, and reset clearing SBU.

### Mac launch shortcut

After the one-time Python 3.12 setup and dependency installation described above, double-click `Start.command` to launch this copy. It uses `.venv/bin/python` from this folder. Keep the Terminal window open while using the app. Control-C stops it.
