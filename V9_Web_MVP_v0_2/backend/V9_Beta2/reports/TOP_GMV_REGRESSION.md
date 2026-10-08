# Top GMV regression evidence

PASS: one positive + zero No Activity; multiple positives + zero No Activity/Closed/Data Review; all zero empty state; one positive alone; more than six positives retains Top 6; positive UNKNOWN and MISSING_CURRENT excluded.

Additional PASS: NaN, positive/negative infinity and negative GMV excluded; records outside current population excluded; selection leaves the analysis frame unchanged; reported-partner denominator retained.

PHARMACY abc: original real deck found in Desktop/PHARMACY_OTC Beta Testing/abc.pptx. Its slide 13 displays Chabua Amirejibi Highway €11,211 and Varketili €0 / No Activity, labeled Top 2. The Beta2 presentation replay uses those displayed values and the actual Beta2 selection/render functions. Output: only Chabua, €11,211, Top 1, 100.0%; reported partner GMV remains €11,211.

Evidence: tests/abc_evidence.json records original source hash and extracted text. tests/fixtures/abc_reference.pptx preserves the source. validation/V9_Beta2_PHARMACY_abc_presentation_replay.pptx retains the real deck and replaces Top GMV, plus approved version/display-label changes. This is a real-deck presentation replay, not a raw-workbook analytical replay: the original Pharmacy workbook was not supplied.

Existing incomplete-current-coverage share qualification is preserved. It can suppress a share when the denominator is not assessable; the denominator is never replaced by the sum of eligible stores.
