# V9_Beta2 regression report

Final suite: **301 passed, 0 failed, 0 errors, 0 skipped**. This consists of 239 carried-forward tests with documented contract/snapshot updates and 62 Beta2 tests. Full test names and results: beta2_full_tests.log. Runtime versions: runtime.json.

The unedited extracted baseline run was **230 passed, 8 failed, 1 error (239 total)**. Preserve this distinction: this was not an initially green, untouched suite. Six failures were stale source/export integrity checks referring to earlier releases or earlier input workbooks; one was the superseded partial-uptime assertion; one was an aggregate freeze check. The error came from assigning infinity to an integer test column under pandas 3.0.5. No analytical formula was altered to resolve these failures.

Test migrations:
- Explicitly replace zero-GMV eligibility expectations and the empty-state text with the approved contract.
- Update partial-uptime expectation to assessed mean plus coverage, matching current baseline source and the user's finalized contract.
- Cast only the infinity test's injected GMV column to float for current pandas compatibility.
- Update the visible-version assertion.
- Keep historical hash manifests in historical_test_manifests/. Current snapshots include only reviewed release changes. Original scoring golden expected values remain unchanged.
- Capture analytical export hashes independently from the extracted baseline, using the same runtime and inputs. Legacy export checks explicitly use tests/beta1_1_benchmark_reference.xlsx. Do not compare updated production benchmark history byte-for-byte with the old workbook.
- Preserve nine independent full-output fixtures and baseline module hashes; new tests compare the release to these captures.

Production dataset tests cover all 43 SBUs, exact same-month lookup, canonical discovery, unknown-name failure and source missingness. Top GMV covers the six required cases plus nonfinite, negative, missing, foreign-population, denominator and real-deck abc evidence. FLOWERS, uptime and lifecycle conflicts pass.

The bundled artifact Python lacked matplotlib; application tests ran in the available Python 3.14.7 environment (exact version in runtime.json). This is an additional tested runtime, not a claim that the older requirements-tested.txt environment was reproduced.
