"""One analysis result feeds rankings, recommendations, reviews and exports."""
from dataclasses import asdict, dataclass
import math

import numpy as np
import pandas as pd

import config as cfg
from data_pipeline import D, N, T, G, U, DataBundle, DataIssue, load_data, period_row, present
from scoring import METRICS, score_metrics, summarize_scores
from store_status import add_lifecycle, current_store_rows


@dataclass
class AnalysisResult:
    data: DataBundle
    stores: pd.DataFrame
    metrics: pd.DataFrame
    opportunities: pd.DataFrame
    actions: list[dict]
    reviews: list[dict]
    summary: dict

    @property
    def settings(self):
        return self.data.settings


def issue_text(metric, conversion_label="CVR"):
    name = conversion_label if metric.metric == "CVR" else metric.metric
    if metric.raw_rate is None:
        return f"{name}: not assessed ({metric.reason})"
    if metric.metric == "Uptime" and not metric.eligible:
        return f"Observed uptime {metric.raw_rate:.1%}; verify configured opening hours"
    target = "target" if metric.metric == "Uptime" else "SBU"
    b = f"{metric.benchmark:.1%}" if metric.benchmark is not None else "unavailable"
    return f"{name} {metric.raw_rate:.1%} vs {target} {b}"


def _classification(row, metrics, median_gmv):
    if row["Store Status"] != "Active":
        return row["Store Status"], "Data review" if row["Data Quality"] != "OK" else "Not applicable"
    cvr = next(m for m in metrics if m.metric == "CVR")
    if cvr.state == "Missing" or cvr.denominator is None or cvr.denominator <= 0:
        commercial = "Conversion not assessed"
    elif cvr.denominator < cfg.CRITICAL_CVR_MIN_SESSIONS:
        commercial = "Limited session evidence"
    elif cvr.adjusted_rate is not None and cvr.benchmark is not None and cvr.adjusted_rate >= cvr.benchmark:
        commercial = "Top Performer" if present(median_gmv) and present(row[G]) and row[G] >= median_gmv else "Growth Potential"
    elif (cvr.relative_gap or 0) >= .10:
        commercial = "Conversion Opportunity"
    else:
        commercial = "Stable"
    ops = [m for m in metrics if m.metric != "CVR"]
    if row["Data Quality"] != "OK" or any(m.state == "Missing" for m in ops if m.eligible):
        operational = "Data review"
    elif any(m.critical_flag for m in ops if m.eligible):
        operational = "Operational Risk"
    elif any((m.severity or 0) > 0 for m in ops if m.eligible):
        operational = "Watch"
    elif any(m.metric == "Uptime" and not m.eligible and (m.raw_rate is None or m.raw_rate < cfg.UPTIME_TARGET) for m in ops):
        operational = "Opening-hours review"
    else:
        operational = "Healthy"
    return commercial, operational


def _review_rows(row, metrics, settings):
    reviews = []
    sid, store = row["Store ID"], row["Store Address Address"]
    def add(kind, issue, action, order, metric=""):
        reviews.append({"Store ID": sid, "Store": store, "Type": kind, "Issue": issue,
                        "Action": action, "Metric": metric, "Sort": order,
                        "Known Priority": row.get("Known Priority", 0), "Owner": "", "Deadline": ""})
    if row["Data Quality"] != "OK" or row["Scoring Status"] == "Incomplete":
        missing = [m.metric for m in metrics if m.eligible and m.state == "Missing"]
        detail = row["Store Status Reason"] if row["Data Quality"] != "OK" else "Missing scoring evidence: " + ", ".join(missing)
        add("Data quality", detail, "Reconcile current activity, lifecycle, missing inputs and benchmark coverage", 0)
    if row["Store Status"] == "No Activity" and row.get("Lifecycle Status") != "not launched":
        add("Activity review", row["Store Status Reason"], "Confirm listing status and investigate absent demand or order activity", 1)
    if row["Store Status"] == "Closed":
        if row["Closure Evidence"] == "Inferred":
            add("Closure verification", row["Store Status Reason"], "Confirm lifecycle status before treating closure as permanent", 1)
        return reviews
    if row["Store Status"] != "Active":
        return reviews
    for m in metrics:
        if m.metric == "Uptime" and not m.eligible:
            if m.raw_rate is None or m.raw_rate < cfg.UPTIME_TARGET:
                add("Opening-hours hygiene", issue_text(m), m.action, 3, m.metric)
            continue
        if m.critical_flag:
            denominator = "" if m.denominator is None else f"; denominator {m.denominator:,.0f}"
            add("Critical observation", issue_text(m, settings.conversion_label) + denominator,
                m.action + "; verify the sample before escalation", 2, m.metric)
        elif m.metric == "Uptime" and m.eligible and m.raw_rate is not None and m.raw_rate < cfg.UPTIME_TARGET and row.get("Eligible Opportunity") is not True:
            add("Availability review", issue_text(m), m.action, 4, m.metric)
    return reviews


def analyze(data):
    settings = data.settings
    add_lifecycle(data)
    from coverage_guard import add_store_coverage
    add_store_coverage(data)
    current = current_store_rows(data)
    active = current[(current["Store Status"] == "Active") & (current[D] > 0)]
    median_gmv = active[G].median() if not active.empty else np.nan
    rows, metric_rows, review_rows = [], [], []
    for _, source in current.iterrows():
        row = source.to_dict()
        history = data.store_monthly[data.store_monthly["Store ID"] == row["Store ID"]]
        metrics = score_metrics(row, data.benchmark_row, history, data.reporting_period, settings, data.benchmark_period)
        row.update(summarize_scores(row, metrics, settings))
        commercial, operational = _classification(row, metrics, median_gmv)
        row.update({"Commercial Status": commercial, "Operational Status": operational})
        primary = next((m for m in metrics if m.metric == row["Main Driver"]), None)
        row["Main Issue"] = issue_text(primary, settings.conversion_label) if primary else "No assessed KPI-recovery gap"
        if row["Scoring Status"] == "Incomplete":
            row["Main Issue"] = "Assessment incomplete; see review list"
        elif row["Store Status"] == "Closed":
            row["Main Issue"] = row["Store Status Reason"]
            row["Recommended Focus"] = "Confirm closure" if row["Closure Evidence"] == "Inferred" else "No routine KPI-recovery action"
        elif row["Store Status"] == "No Activity":
            row["Main Issue"] = row["Store Status Reason"]
        row["Confidence"] = " / ".join(f"{m.metric} n={m.denominator:,.0f}, w={m.confidence_weight:.0%}" if m.state == "Assessed" and m.raw_rate is not None else f"{m.metric} rate unavailable / not assessed · n={m.denominator:,.0f}"
                                        for m in metrics if m.denominator is not None and m.confidence_weight is not None)
        rows.append(row)
        for m in metrics:
            metric_rows.append({"Store ID": row["Store ID"], "Store": row["Store Address Address"],
                                "Period": data.reporting_period, **m.record()})
        review_rows.extend(_review_rows(row, metrics, settings))
    stores = pd.DataFrame(rows)
    metric_table = pd.DataFrame(metric_rows)
    ranked = stores[stores["Eligible Opportunity"]].sort_values(
        ["Opportunity Score", "Business Impact Score", "Performance Severity Score", "Store ID"],
        ascending=[False, False, False, True], kind="mergesort").copy()
    ranked["Rank"] = range(1, len(ranked) + 1)
    opportunities = ranked.head(settings.top_opportunities).copy()
    actions = []
    for _, row in opportunities.iterrows():
        primary = metric_table[(metric_table["Store ID"] == row["Store ID"]) & (metric_table["metric"] == row["Main Driver"])].iloc[0]
        actions.append({"Store ID": row["Store ID"], "Store": row["Store Address Address"],
                        "Metric": row["Main Driver"], "Issue": row["Main Issue"], "Action": primary["action"],
                        "Intended Effect": primary["intended_effect"], "Priority": row["Opportunity Score"],
                        "Metric Priority": primary["paired_priority"], "Exposure": primary["exposure"],
                        "Owner": "", "Deadline": ""})
    reviews = sorted(review_rows, key=lambda r: (r["Sort"], -(r["Known Priority"] or 0), r["Store ID"], r["Metric"]))
    summary = {
        "version": "V9_dev6_1", "reporting_period": data.reporting_period.strftime("%Y-%m"),
        "benchmark_period": data.benchmark_period.strftime("%Y-%m") if data.benchmark_period is not None else None,
        "conversion_contract": settings.conversion_description, "priority_model": settings.priority_model,
        "priority_threshold": settings.min_priority, "threshold_status": "Provisional; requires business ranking calibration",
        "exposure_definition": "Conservative maximum of overlapping metric exposure proxies; not incremental orders or a financial forecast",
        "sbu": settings.partner_sbu, "known_stores": len(stores),
        "status_counts": stores["Store Status"].value_counts().to_dict(),
        "incomplete_assessments": int((stores["Scoring Status"] == "Incomplete").sum()),
        "eligible_opportunities": len(ranked), "displayed_opportunities": len(opportunities),
        "primary_actions": len(actions), "review_items": len(reviews),
        "partner_median_gmv": float(median_gmv) if present(median_gmv) else None,
        "input_hashes": data.input_hashes,
        "data_quality_counts": {level: sum(i.level == level for i in data.issues) for level in ("error", "warning", "info")},
        "store_coverage": data.coverage.to_dict("records"),
        "benchmark_note": "SBU membership/self-inclusion is not identifiable from aggregate input",
        "prior_model_note": "Original TC51–TC100 fixtures and Dev4 source were not available; no historical pass-rate claim",
    }
    return AnalysisResult(data, stores, metric_table, opportunities, actions, reviews, summary)


def run_analysis(settings=None):
    return analyze(load_data(settings))
