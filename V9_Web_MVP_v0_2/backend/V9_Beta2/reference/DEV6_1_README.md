# V9_dev6.1

Dev6-ის კონტროლირებადი hardening და Store Diagnostics-ის ვიზუალური განახლება. სკორინგის ძირითადი ფორმულები, calibration, SBU წესები და lifecycle engine უცვლელია.

## გაშვება macOS / Python 3.14-ზე

გახსენით ZIP, ტერმინალიდან გადადით `V9_dev6_1` საქაღალდეში:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

შეიქმნება `Partner_Business_Review_V9_dev6_1.pptx` და შესაბამისი `_audit` საქაღალდე. სრული რეგრესიული შემოწმება:

```bash
python validate.py
```

SBU-ს შეცვლა და სხვა ფაილების გამოყენება:

```bash
python main.py --sbu PHARMACY_OTC --partner my_partner.xlsx --benchmark my_sbu.xlsx --output review.pptx
python main.py --analysis-only
```

**ოფიციალური CVR დაფიქსირებულია:** მაღაზიის reported `% CVR`; partner/SBU დონეზე — სესიებით შეწონილი reported CVR. Delivered/session მხოლოდ დიაგნოსტიკაა. ალტერნატიული CVR სკორინგის რეჟიმები გამორთულია.

**Priority ≥ 5 დროებითი ზღვარია და უცვლელად რჩება.** Paired model წარმოების ნაგულისხმევი მოდელია. `--priority-model simple_product` კვლევით ალტერნატივას ჩართავს; ასეთი deck ყველა სლაიდზე `EXPERIMENTAL / CHALLENGER MODEL` ნიშნით იქმნება. ორივე ქულა ყოველთვის ინახება audit ექსპორტში.

## Input and scoring contract

Default input grain is one store/month row. Required fields: Month, Year, Store ID (or Store Address Address), # Delivered Orders, Sessions Store, Number of Total Orders, Number of Pna Orders, Number of Canceled Orders Due to Partner, € GMV, % Uptime, % CVR. SBU input additionally requires Store Sub Business Unit. Optional display metadata: Store Name, City, Location. Use stable Store IDs for renames.

Counts are finite nonnegative integers; rates default to fractions. Explicit `95%` strings work; percent-unit files require `Settings(percentage_units="percent")`. Missing values remain missing. Invalid dates, impossible counts and duplicate store/month rows reject the run. Only genuinely additive partitions should use `allow_partitioned_rows=True`; their reported CVR is session-weighted and their uptime remains an unweighted mean. Source workbooks are not modified.

Official store CVR is its reported value. Partner/SBU CVR is `sum(reported CVR × sessions) / sum(sessions)`. A missing reported CVR on a positive-session row makes aggregate CVR incomplete; it never falls back to delivered/session. Zero-session rows add no weight to partner/SBU CVR. Without a positive aggregate denominator the aggregate rate remains unavailable. Single-store observations remain visible even if their denominator is missing/zero, while score eligibility follows the unchanged denominator rules. Missing a required column rejects input; missing a required value yields an incomplete assessment where applicable.

PNA = PNA attempts / total attempts; Cancels = partner cancellations / total attempts; AOV = GMV / delivered orders. Delivered / Sessions Diagnostic and CVR Reconciliation Gap are exported separately. PNA may overlap deliveries/cancellations, so exposure is not guaranteed recoverable orders.

Existing calibration is unchanged: CVR/PNA/Cancels k=150/30/10, weights .30/.30/.25/.15, all Dev5/Dev6 anchors, 50% dominant-KPI protection, 95% uptime target and raw critical thresholds. For eligible metrics `q_i = severity_i × H(exposure_i)/100`; paired Priority is the greater of the weighted mean of q and half its maximum. Standalone Severity follows the original aggregation; headline Impact is the maximum component impact. Missing required metrics leave official scores unassessed. Full-precision ranking, threshold 5, six displayed opportunities, tie ordering and singular issue-based actions remain unchanged. Flags add no score points.

## Coverage and presentation safeguards

A store is expected from its first observed month onward. All historically known stores stay in that conservative expected roster; an absent row is not treated as a zero or as a confirmed exit. New stores are not backfilled before their first observation. No separate authoritative store-roster input was supplied, so the system cannot detect a store that has never appeared in the data.

For every calendar month, export expected/present/missing counts and missing IDs/names. If either endpoint of a partner MoM/YoY comparison is incomplete, suppress that comparison and its growth/decline narrative. Raw totals remain unchanged and are labeled Partial Store Coverage. A coverage detail slide identifies affected periods/stores. Partner-vs-SBU levels can still appear with the coverage warning; no like-for-like replacement formula is introduced. The rule also guards partner share comparisons. `partner_comparisons.csv` exports the same comparability decisions and null changes.

Current/future incomplete months still reject by default. `--allow-partial-period` explicitly permits them and adds PARTIAL PERIOD — PROVISIONAL ANALYSIS to every slide. This is a disclosure, not a rescaling of partial-month data or a threshold adjustment.

Store Diagnostics displays state badges, business context, four KPI cards with references and gaps, three score cards, independent driver labels, denominator-based confidence indicators, a six-calendar-month main-KPI trend, critical/lifecycle evidence and one recommendation. Missing points stay missing; at least two valid trend points are required. The latest benchmark is a labeled reference line, not an assertion about historical benchmark values. Incomplete assessments use Leading known issue and Not assessed. FLOWERS uptime explicitly says Hygiene only — excluded from business Priority. Closed/No Activity dashboards explain lifecycle and zero routine recovery Priority. No second recommendation system was added.

The numeric Main Driver field is retained as diagnostic evidence for incomplete assessments; user-facing wording never calls it a finalized business action. Confidence percentages are shown only for an assessed, available rate. The underlying shrinkage weights remain available in metric records for audit.

## Runtime and verification

Actual execution: **Linux x86_64, CPython 3.14.6**. Direct pins: pandas 2.3.3, NumPy 2.3.5, openpyxl 3.1.5, python-pptx 1.0.2, Matplotlib 3.10.8, Pillow 12.3.0. Full transitive lock: requirements-tested.txt. Only pandas changed from the Dev6 direct pins (2.2.3 → 2.3.3).

[pandas 2.3.3 supports Python 3.14](https://pandas.pydata.org/docs/whatsnew/v2.3.3.html); [NumPy 2.3.5 supports 3.11–3.14](https://numpy.org/doc/2.3/release/2.3.5-notes.html). The dependency resolver also successfully resolved binary-only packages for Python 3.14 / macOS ARM64; see validation/macos_arm64_resolution.txt. That is a dependency-availability check, not native macOS execution or PowerPoint-for-Mac certification. The supplied workbook's default-style warning is cosmetic and unchanged. Install Montserrat for closest typography to the retained Glovo style.

The original Dev6 49-test suite passed on the untouched baseline. Dev6.1 retains all 49 test slots: its alternate-CVR test is updated to assert rejection under Change A; one presentation assertion now accepts uppercase status badges under Change C. All KEEP tests remain unchanged. Additional A–G tests and an 80-store frozen Dev6 comparison cover numerical scores, flags, ordering and actions under the new runtime. `scoring.py` and `store_status.py` are byte-identical to Dev6. This is implementation regression evidence, not threshold calibration or proof of business-optimal ranking. Original TC51–TC100 fixtures remain unavailable.

See validation/REGRESSION_RESULT.md for final counts/visual checks and CHANGELOG.md for the specification mapping. Use `python tests/build_ux_examples.py validation/ux_examples` to reproduce the visual state fixtures. The V8.1 reference is historical and is not imported. No rollout or GitHub publication is part of this release.
