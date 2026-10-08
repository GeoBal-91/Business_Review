# V9_Beta2 SBU compatibility

PASS: 43/43 values resolve through the existing exact-match loader. August 2026 is selected for every current-period test. Each SBU retains 12 months of history. Unknown names raise DataValidationError; no alternate SBU fallback exists.

OLD: 312 rows, 26 SBUs. NEW: 516 rows, 43 SBUs. Same ordered 29-column schema. No removals.

The NEW source also revises 56 existing cells beyond floating-point rounding, affecting OTHER. See benchmark_value_changes.json. These are supplied data changes, not model recalibration.

| SBU | Availability | August lookup |
|---|---|---|
| ALCOHOL | New | PASS |
| AUTOMOTIVE | Existing | PASS |
| BAKERY_PASTRY | New | PASS |
| BEAUTY_PERSONAL_CARE | Existing | PASS |
| BOOKS | Existing | PASS |
| BUTCHERY_CHARCUTERIE | New | PASS |
| CBD | Existing | PASS |
| COFFEE_TEA | New | PASS |
| CONVENIENCE | New | PASS |
| COVID_TEST | Existing | PASS |
| DAIRY_PRODUCTS | New | PASS |
| ELECTRONICS | Existing | PASS |
| FASHION | Existing | PASS |
| FISHERY | New | PASS |
| FLOWERS | Existing | PASS |
| FROZEN_FOOD | New | PASS |
| FRUITS_VEGETABLES | New | PASS |
| GOURMET | New | PASS |
| HOME_DECORATION | Existing | PASS |
| ICE_CREAM | New | PASS |
| INDUSTRIAL | Existing | PASS |
| INTERNATIONAL | New | PASS |
| JEWELRY | Existing | PASS |
| KIDS_BABIES | Existing | PASS |
| LOCAL_MARKET | New | PASS |
| ORGANIC_BIO | New | PASS |
| OTHER | Existing | PASS |
| PARA_PHARMACY | Existing | PASS |
| PETS | Existing | PASS |
| PHARMACY_OTC | Existing | PASS |
| PHARMACY_RX | Existing | PASS |
| SERVICES | Existing | PASS |
| SEX_SHOP | Existing | PASS |
| SPORTS_OUTDOORS | Existing | PASS |
| STATIONERY_DIY | Existing | PASS |
| SUPERMARKET | New | PASS |
| SWEETS | New | PASS |
| TOBACCO_HEATED_PRODUCTS | Existing | PASS |
| TOYS_GAMES | Existing | PASS |
| TRADITIONAL_TOBACCO | Existing | PASS |
| VAPES | Existing | PASS |
| VISION | Existing | PASS |
| WELLNESS | New | PASS |

ICE_CREAM and PHARMACY_RX have missing August CVR in the source. These values remain missing and never borrow another SBU’s CVR.

Backend API: `from sbu_catalog import supported_sbus`; `supported_sbus()` returns a sorted tuple read explicitly from the production workbook. Pass a DataFrame or alternate path for a web request. Imports do not load workbooks. CLI: `python main_v2_1.py --list-sbus`.

Architecture audit: data_pipeline.prepare_input already filters exact normalized SBU names. No analytical allowlist or enum rejects new values. Settings normalizes the selected string. SBU_ASSETS in ppt_core.py maps optional artwork only, never availability. New SBUs use the generic engine and may lack decorative icons. FLOWERS remains the intentional commercial uptime exception.
