# Web MVP smoke-test report

Date: 2026-09-15. Environment: macOS / Apple Silicon, Python 3.12.14, Streamlit 1.62.0, original six Beta2 dependency pins. Exact installed versions: requirements-lock.txt.

## Results

**7/7 integration test groups passed** (`python -m unittest discover -s tests -v`, 44.888 seconds).

| Test group | Evidence |
| --- | --- |
| SBU catalog | 43 sorted unique entries from the actual backend API; PHARMACY_RX included |
| Valid metadata | JEWELRY example: August 2026, one store, absent name reported honestly; added explicit partner-name column detected |
| Blocking validation | Missing CVR column, duplicate grain, malformed rate, negative count, invalid month, future/partial period, unknown SBU, missing benchmark metric, incompatible benchmark date, multiple explicit partners rejected |
| Upload boundaries | Empty/malformed/oversized workbook and logo inputs rejected |
| Cleanup | Validation failure, forced timeout and worker-start failure leave no request directories |
| Generation/parity/isolation | Two simultaneous real Beta2 runs with red/blue test logos; each PPTX embeds its own logo; all audit CSV bytes exactly match the untouched main_v2_1.py analysis-only CLI; backend fingerprint unchanged; temporary directories empty after success |
| Streamlit workflow | AppTest uploads real XLSX/logo; generation disabled until valid; real generation produces both downloads; changing SBU to ICE_CREAM blocks generation and removes downloads; Clear resets uploads/results |

All **282 frozen baseline files** match the uploaded ZIP byte-for-byte, including assets, benchmark, source and supplied historical evidence. This is stronger than checking only scoring modules.

The final logo uploader's visible 5 MB limit was followed by a targeted rerun of the full Streamlit workflow test.

## Additional checks

- Started the real Streamlit server on localhost:8511 and opened the page in the in-app browser. The upload interface rendered; end-to-end widget behavior was exercised by AppTest.
- The generated JEWELRY PPTX has **21 slides** and opens through python-pptx.
- Independent OOXML package-integrity validator: **PASS, zero findings**.
- All 21 slides rendered to PDF/PNG with bundled LibreOffice. The cover was inspected at full size and the deck scanned in a contact sheet; the distinct uploaded test logo was correctly placed. No deck layouts were edited.
- The local LibreOffice rendering substituted fonts. This is not a claim of a full PowerPoint visual regression test; view with Montserrat installed for the intended Beta2 typography.

## Scope and remaining limits

- The original archive reports 301/301 backend release tests. That historical result is retained, **not claimed as newly rerun**. The new checks exercise integration, exact audit parity and complete-source integrity.
- Real integration generation used the supplied JEWELRY workbook; red/blue logos and malformed input variants are test fixtures. This is not a fresh raw-data validation of all 43 SBU scoring cases.
- No partner name can be inferred from the supplied sample's address-only schema. The app explicitly displays that absence.
- August CVR is missing for ICE_CREAM and PHARMACY_RX in the frozen source. The UI blocks those month/SBU combinations; it does not alter the benchmark or invent fallback values.
- Crash/force-kill cleanup, large multi-user load, other operating systems and native PowerPoint rendering were not tested.
- Login, database, history, hosting and direct Looker API are outside this MVP.
