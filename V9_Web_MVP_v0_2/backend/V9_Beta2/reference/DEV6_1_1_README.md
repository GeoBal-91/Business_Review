# V9_dev6.1.1

A controlled presentation patch to the completed Dev6.1 release. The analytical/scoring architecture remains frozen. See `CHANGELOG.md`, `validation/REGRESSION_RESULT.md` and `RELEASE.json`.

## Run

From the extracted `V9_dev6_1_1` folder, using Python 3.14:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py --output Partner_Business_Review_V9_dev6_1_1.pptx
python validate.py
```

The fresh PPTX and its `_audit` directory are included. The command above explicitly names the presentation patch output; the existing CLI/config defaults and analytical audit version remain Dev6.1. Only the presentation release label changes. Other partner/SBU inputs still use the existing `--partner`, `--benchmark` and `--sbu` options.

No dependency pins changed. The validated environment is CPython 3.14.6 / Linux x86_64; exact versions are recorded in the regression report and `requirements-tested.txt`. No native macOS run is claimed.

## Presentation changes

- **Store Performance Matrix:** fixed store colors assigned by sorted stable Store IDs; full-name/address legend in a dedicated right-side area; no point labels. Colors do not encode performance. Long legends continue at the same readable text size on further matrix slides with the same plot and reference lines. GMV, official CVR, plotted-store selection, median/reference lines and analytical footnote are unchanged.
- **Top GMV Stores:** the same six-store selection and ordering, an editable table, the supplied crown artwork and a dynamic concentration highlight. The share is displayed stores' GMV divided by current partner GMV. Actual displayed N is used, including a singular-store case. Missing/zero GMV or partial current coverage produces an explicit unavailable/not-assessed share.
- **How to Read This Review:** eight illustrated cards and a Key takeaway / Remember panel. All methodology caveats remain, including actual benchmark period, peer-composition availability, provisional threshold, exposure overlap, healthy-history uptime methodology and the FLOWERS exclusion.
- **Current-coverage CVR guard:** an incomplete current partner roster suppresses directional Partner-vs-SBU CVR interpretation in the Executive Summary. Raw partner CVR and SBU CVR remain visible. A gap only in historical coverage does not suppress a complete current comparison.

Recommendations, Action Plan logic and Store Diagnostics are unchanged. All existing Dev6.1 tests remain unedited. No new analytical metric or forecast is introduced; the GMV share is a presentation statistic only.

Legends, table text, cards and other text remain editable PowerPoint elements. The matrix plot retains the existing data-generated image approach; supplied artwork is embedded unchanged.

## UX examples

```bash
python tests/build_presentation_examples.py validation/ux_examples
```

This produces a 12-store example and the missing-large-store example, with normal audit exports. They are synthetic fixtures and their covers say so. The principal Partner Business Review uses the unchanged bundled workbooks. Selected screenshots accompany the UX examples ZIP.

The complete Dev6.1 input/scoring documentation is retained in `reference/DEV6_1_README.md`. Priority ≥5 remains provisional. No threshold calibration, Recommendations redesign or rollout is part of this patch.
