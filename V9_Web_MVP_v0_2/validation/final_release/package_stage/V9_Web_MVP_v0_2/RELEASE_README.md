# Final release — 6 October 2026

Only Cover and Thank You were redesigned. Analytical code and all other approved slides are preserved. Partner Share Evolution remains 20.0 cm wide.

## Run

Validation used Python 3.14.7. Use the matching tested dependency list:

```
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements-final-tested.txt
.venv/bin/python -m streamlit run app.py
```

The retained original README/launcher mention the earlier Python 3.12 setup. This release note records the actual final validation environment. The historical lock is preserved; requirements-final-tested.txt records the installed versions used for validation. A fresh dependency installation has not been tested. Fonts Montserrat and Noto Sans Georgian must be available for matching rendering. PowerPoint rendering was not independently tested; visual QA used LibreOffice.

The application retains its existing localhost binding. Hosting configuration and deployment remain outside this presentation release.

All runtime Python modules, benchmark workbook, logos and approved transparent PNG assets are included. Development tests, frozen historical snapshots, generated presentations/audits, temporary renders and virtual environments are excluded. Full validation evidence remains in the source workspace under validation/final_release.

## Validation disposition

37/37 web/presentation/UI tests passed. Five actual worker decks passed presentation preservation, icons, dynamic fields and audit checks. All 110 analytical audit files matched the external engine on identical inputs and explicit SBU after normalizing temporary paths and the independently verified default-SBU-only config hash.

Historical suites: bundled backend 299/301 passed (two old logo hash expectations); external reference 295/301 passed (six historical config/sample snapshot expectations). These differences existed before this task. Neither baseline was modified to force these tests to pass. No new analytical regression was found.

SOURCE_MANIFEST_SHA256.json records SHA-256 for every packaged file except the manifest itself. Its own SHA-256 is recorded beside the ZIP in the release metadata.
