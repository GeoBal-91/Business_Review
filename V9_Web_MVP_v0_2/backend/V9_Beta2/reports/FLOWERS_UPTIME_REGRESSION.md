# FLOWERS and uptime evidence

PASS: FLOWERS tests at uptime 0%, 10%, 95% and blank preserve identical commercial Priority, Impact and selected action KPI. Uptime is ineligible for commercial scoring and absent from commercial action records. Existing V2.1 FLOWERS rule regressions pass, including commercial override exclusions. The unchanged scoring, lifecycle and triage settings hashes independently protect the exception. No new SBU exception was added.

PASS: assessed 0% plus blank aggregates to 0%, coverage 1/2; the blank store stays missing. An all-blank eligible cohort has zero assessed stores and no uptime aggregate. A partial known cohort retains its assessed mean and reduced coverage. Contradictory activity plus a closed lifecycle remains Active / Conflict, never silently Closed.

The baseline's old test requiring an entirely missing aggregate for partial coverage contradicted the current source and the finalized user contract. Only that assertion and its test name were updated; data_pipeline.py and store_status.py are unchanged.
