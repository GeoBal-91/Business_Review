# V9_Beta2

- Updated production SBU benchmark workbook: 43 supported SBUs, including 17 additions.
- Exposed dataset-driven SBU discovery for backend/web consumers and --list-sbus CLI access. No Streamlit frontend added.
- Top GMV now requires observed finite positive current-period GMV in the current population. Zero-GMV, UNKNOWN and MISSING_CURRENT rows are excluded.
- Supports Top 1 through Top 6 and the clean empty state: “No positive-GMV stores available for the current period.” Reported partner GMV is unchanged.
- Preserved the frozen analytical engine, FLOWERS commercial uptime exclusion, finalized partner uptime coverage and V2.1 classification. No scoring/classification recalibration.
- Standardized the isolated methodology display label to Primary Action KPI. Export field keys retain compatibility.
- Updated release metadata and added compatibility, integrity and presentation regression evidence.
