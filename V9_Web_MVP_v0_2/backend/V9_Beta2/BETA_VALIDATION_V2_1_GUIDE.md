# AM validation — V2.1

Use `Beta_Validation_Stores_V2_1.csv` from the relevant deck's audit folder. Keep a separate reviewed copy: regenerating a deck writes fresh blank templates.

Priority/Severity/Impact and original Opportunity Rank/Eligible Opportunity still describe frozen Beta analytics. Business Classification, Action Reason and Triage Rank describe V2.1. A store can legitimately have Priority 3.56 and ACTION / Business Materiality Override. Do not adjust scores or overwrite engine fields to express an AM judgment.

Fill existing AM fields and the additional fields:

- AM_Business_Classification_Agree: Yes / Partly / No.
- AM_Action_Reason_Agree: Yes / Partly / No.
- AM_Operational_Driver_Agree: Yes / Partly / No; judge the hypothesis, not a claim of proven causation.
- AM_Recovery_Context_Comment: free text, especially persistence and operational context for low-scale ACTION.

Existing AM_Should_Be_Priority, AM_Rank, AM_Main_Action_KPI_Agree, AM_Action_Relevance_1_5, AM_Important_Opportunity_Missed, AM_Should_Not_Be_Pitched and AM_Comment remain blank for independent judgment. The partner-level template remains `Beta_Validation_Partner.csv`.

Review all classified stores, not only the six selected main-page actions. Pay attention to override cases, MONITOR cases near entry boundaries, HEALTHY tolerance and UNCLASSIFIED data/lifecycle rows. FLOWERS uptime is hygiene only. Small realized GMV is context, not an automatic rejection. A Critical Flag is not automatically ACTION.

Record wrong class, wrong main KPI, irrelevant action, missed action and possible duplicate identity separately. Never merge stores without reliable IDs. Cross-profile calibration summaries may use an explicit duplicate alias only after matching contents/identities are verified.

The real seven-SBU retrospective population was not bundled. This release's synthetic controls demonstrate rule behavior; they must not be used to report retrospective AM agreement rates. The Priority ≥5 base rule remains provisional, and isolated tolerance/scale settings require confirmation against real labelled cases.
