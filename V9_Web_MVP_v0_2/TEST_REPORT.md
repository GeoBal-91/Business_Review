# Web v0.2 — verification

Final local run: 8 tests passed in 41.532 seconds.

- 43-SBU catalog and partner metadata.
- Schema, rate, count, period, single-partner and same-month benchmark blocking.
- File/logo limits, malformed uploads, worker failure and timeout cleanup.
- Real PPTX generation, two-logo isolation, and byte-for-byte CSV audit parity with the original CLI.
- Streamlit upload → selection → validation → generation → two downloads → input-change invalidation → reset.
- Logo changes reuse data validation; invalid logos block generation; SBU changes rerun validation; reset clears SBU.
- All 282 frozen Beta2 files match the supplied baseline.

Browser checks: actual export/logo upload, SBU search, validation notes, missing partner-name display, ready-to-generate state, and generation progress. Desktop empty-state layout was visually inspected at 1440px with no horizontal overflow and the Generate button visible within a 1000px-high viewport. Earlier responsive and sidebar reopen fixes are retained. This release does not claim a new native PowerPoint review of a real partner deck.

The v0.1 build report is retained separately as TEST_REPORT_V0_1.md.
